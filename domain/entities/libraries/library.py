from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Iterable

from pydantic import PrivateAttr, Field

from domain.entities.borrower import Borrower
from domain.entities.entity import Entity
from domain.entities.libraries.library_fee import LibraryFee
from domain.entities.loan import Loan
from domain.entities.mop_server import MOPServer
from domain.entities.people.person import Person
from domain.entities.thing import Thing
from domain.entities.waiting_lists.waiting_list import WaitingList
from domain.factories import MoneyFactory, WaitingListFactory
from domain.value_items import (
    ID,
    DueDate,
    FeeSchedule,
    FeeStatus,
    LoanStatus,
    Location,
    Money,
    ThingStatus,
    ThingTitle,
    WaitingListType,
)


class Library(Entity, ABC):
    model_config = {"arbitrary_types_allowed": True, "frozen": True}

    library_id: ID
    name: str
    administrator: Person
    location: Location
    waiting_list_type: WaitingListType
    waiting_lists_by_item_id: dict[ID, WaitingList] = Field(default_factory=dict)
    max_fines_before_suspension: Money
    fee_schedule: FeeSchedule
    money_factory: MoneyFactory = Field(default_factory=MoneyFactory)
    default_loan_time: timedelta
    mop_server: MOPServer
    public_url: str | None = None

    _borrowers: list[Borrower] = PrivateAttr(default_factory=list)
    _loans: list[Loan] = PrivateAttr(default_factory=list)

    @property
    def entity_id(self) -> ID:
        return self.library_id

    @property
    @abstractmethod
    def all_things(self) -> Iterable[Thing]:
        pass

    @property
    def available_things(self) -> Iterable[Thing]:
        for thing in self.all_things:
            if thing.status == ThingStatus.READY:
                yield thing

    @abstractmethod
    async def borrow(self, thing: Thing, borrower: Borrower, until: DueDate) -> Loan:
        pass

    @abstractmethod
    async def start_return(self, loan: Loan) -> Loan:
        raise NotImplementedError()

    @property
    def borrowers(self) -> Iterable[Borrower]:
        return self._borrowers

    def add_borrower(self, borrower: Borrower) -> Borrower:
        self._borrowers.append(borrower)
        return borrower

    def can_borrow(self, borrower: Borrower) -> bool:
        if borrower.library_id != self.entity_id:
            return False

        fee_amounts = [
            f.amount for f in borrower.fees if f.status == FeeStatus.OUTSTANDING
        ]
        total_fees = self.money_factory.total(fee_amounts)
        return total_fees <= self.max_fines_before_suspension

    async def reserve_item(self, item: Thing, borrower: Borrower) -> WaitingList:
        if not item.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError

            raise EntityNotAssignedIdError("")

        waiting_list = self.waiting_lists_by_item_id.get(item.entity_id)
        if not waiting_list:
            waiting_list = WaitingListFactory.create_new_list(self, item)
            self.waiting_lists_by_item_id[item.entity_id] = waiting_list

        waiting_list.add(borrower)
        return waiting_list

    def get_loans(self) -> Iterable[Loan]:
        return self._loans

    def add_loan(self, loan: Loan) -> None:
        self._loans.append(loan)

    @staticmethod
    def get_titles_from_items(items: Iterable[Thing]) -> Iterable[ThingTitle]:
        titles = []
        for item in items:
            if not any(t == item.title for t in titles):
                titles.append(item.title)
        return titles

    async def finish_library_return(self, loan: Loan, borrower: Borrower) -> Loan:
        # This has to call FIRST, so the status can be updated to act here
        if (
            loan.status != LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
            or not loan.time_returned
        ):
            from domain.value_items.exceptions import ReturnNotStartedError

            raise ReturnNotStartedError()

        if loan.item.status == ThingStatus.DAMAGED:
            loan.status = LoanStatus.RETURNED_DAMAGED
        else:
            if loan.due_date.date:
                if loan.time_returned > loan.due_date.date:
                    loan.status = LoanStatus.OVERDUE
                else:
                    loan.status = LoanStatus.RETURNED
            else:
                # Should we be able to return things without a date?
                loan.status = LoanStatus.RETURNED

        fee_amount = None
        if loan.item.status == ThingStatus.DAMAGED:
            # Apply the fees
            fee_amount = self.fee_schedule.fee_for_damaged_item(loan)

        if loan.status == LoanStatus.OVERDUE:
            # Calculate the late fee and apply
            fee_amount = self.fee_schedule.fee_for_overdue_item(loan)

        if fee_amount:
            fee = LibraryFee(
                library_fee_id=ID.generate(),
                library_id=self.library_id,
                amount=fee_amount,
                charged_for_id=loan.loan_id,
            )
            fee.status = FeeStatus.OUTSTANDING
            borrower.apply_fee(fee)

        # Is there a waiting list for the item?
        if not loan.item.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError

            raise EntityNotAssignedIdError("")

        if loan.item.entity_id in self.waiting_lists_by_item_id:
            waiting_list = self.waiting_lists_by_item_id[loan.item.entity_id]
            if waiting_list:
                waiting_list.reserve_item_for_next_borrower()

        if loan.item.status == ThingStatus.BORROWED:
            loan.item.status = ThingStatus.READY

        return loan
