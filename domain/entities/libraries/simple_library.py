from typing import List, Optional, Iterable
from datetime import datetime
from domain.entities import Thing, Borrower, Loan, Person
from domain.entities.libraries import BaseLibrary
from domain.entities.lenders import Lender
from domain.entities.factories import IWaitingListFactory, MoneyFactory, FeeSchedule
from domain.services.bidding import BiddingStrategy
from domain.value_items import (
    ThingTitle,
    ThingStatus,
    PhysicalLocation,
    MOPServer,
    LoanStatus,
    DueDate,
    TimeInterval,
    BorrowerNotInGoodStandingError,
    InvalidThingStatusToBorrowError,
    Money
)


class SimpleLibrary(BaseLibrary, Lender):
    def __init__(
        self,
        id: str,
        name: str,
        admin: Person,
        location: PhysicalLocation,
        waiting_list_factory: IWaitingListFactory,
        max_fines_before_suspension: Money,
        loans: Iterable[Loan],
        money_factory: MoneyFactory,
        mop_server: MOPServer,
        fee_schedule: Optional[FeeSchedule] = None,
        default_loan_time: Optional[TimeInterval] = None,
        bidding_strategy: Optional[BiddingStrategy] = None
    ):
        if default_loan_time is None:
            default_loan_time = TimeInterval.from_days(14)

        super().__init__(
            id=id,
            name=name,
            administrator=admin,
            max_fines_before_suspension=max_fines_before_suspension,
            loans=loans,
            money_factory=money_factory,
            mop_server=mop_server,
            default_loan_time=default_loan_time,
            fee_schedule=fee_schedule,
            bidding_strategy=bidding_strategy,
            waiting_list_factory=waiting_list_factory
        )

        self._items: List[Thing] = []
        self.location = location

    def add_item(self, item: Thing) -> Thing:
        self._items.append(item)
        return item

    def get_all_things(self) -> Iterable[Thing]:
        return self._items

    @property
    def items(self) -> Iterable[Thing]:
        return self._items

    def borrow(self, item: Thing, borrower: Borrower, until: Optional[DueDate] = None) -> Loan:
        if item.status != ThingStatus.READY:
            raise InvalidThingStatusToBorrowError(item.status)

        if not self.can_borrow(borrower):
            raise BorrowerNotInGoodStandingError()

        if not until:
            until = DueDate(self.default_loan_time.from_now())

        loan = Loan(
            loan_id=None,
            item=item,
            borrower=borrower,
            due_date=until,
            status=LoanStatus.BORROWED,
            location=self.location,
            date_returned=None
        )

        item.status = ThingStatus.BORROWED
        self.add_loan(loan)
        return loan

    @property
    def all_titles(self) -> Iterable[ThingTitle]:
        return self.get_titles_from_items(self.items)

    @property
    def available_titles(self) -> Iterable[ThingTitle]:
        available_items = [i for i in self.items if i.status == ThingStatus.READY]
        return self.get_titles_from_items(available_items)

    def preferred_return_location(self, item: Thing) -> PhysicalLocation:
        return self.location

    def start_return(self, loan: Loan) -> Loan:
        loan.status = LoanStatus.RETURN_STARTED
        loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
        loan.date_returned = datetime.now()
        return loan
