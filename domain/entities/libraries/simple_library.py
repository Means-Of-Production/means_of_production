from datetime import datetime
from typing import Iterable

from domain import Location
from domain.entities.borrower import Borrower
from domain.entities.lenders.lender import Lender
from domain.entities.libraries.library import Library
from domain.entities.loan import Loan
from domain.entities.people.person import Person
from domain.entities.thing import Thing
from domain.value_items import ID, DueDate, LoanStatus, ThingStatus, ThingTitle
from domain.value_items.exceptions import (
    BorrowerNotInGoodStandingError,
    InvalidThingStatusToBorrowError,
)


class SimpleLibrary(Library, Lender):
    library_id: ID
    name: str
    administrator: Person
    _items: list[Thing] = []

    @property
    def entity_id(self) -> ID:
        return self.library_id

    def add_item(self, item: Thing) -> Thing:
        self._items.append(item)
        return item

    @property
    def all_things(self) -> Iterable[Thing]:
        return self._items

    @property
    def items(self) -> Iterable[Thing]:
        return self._items

    async def borrow(
        self, thing: Thing, borrower: Borrower, until: DueDate | None = None
    ) -> Loan:
        # Check if available
        if thing.status != ThingStatus.READY:
            raise InvalidThingStatusToBorrowError(thing.status)

        # Check if borrower in good standing
        if not self.can_borrow(borrower):
            raise BorrowerNotInGoodStandingError()

        if not until:
            until = DueDate(date=datetime.now().date() + self.default_loan_time)

        # Make loan
        loan = Loan(
            loan_id=ID.generate(),
            item=thing,
            borrower_id=borrower.entity_id,
            due_date=until,
            return_location=self.location,
            time_returned=None,
        )
        loan.status = LoanStatus.BORROWED
        thing.status = ThingStatus.BORROWED

        self.add_loan(loan)
        return loan

    @property
    def all_titles(self) -> Iterable[ThingTitle]:
        return self.get_titles_from_items(self.items)

    @property
    def available_titles(self) -> Iterable[ThingTitle]:
        available_items = [i for i in self.items if i.status == ThingStatus.READY]
        return self.get_titles_from_items(available_items)

    @property
    def preferred_return_location(self) -> Location:
        return self.location

    async def start_return(self, loan: Loan) -> Loan:
        # Simple library does not have an acceptance step, only the library starts returns!
        loan.status = LoanStatus.RETURN_STARTED
        loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
        loan.time_returned = datetime.now()
        return loan

    async def finish_library_return(self, loan: Loan, borrower: Borrower) -> Loan:
        return await self.finish_return(loan)

    async def finish_return(self, loan: Loan) -> Loan:
        loan.status = LoanStatus.RETURNED
        return loan
