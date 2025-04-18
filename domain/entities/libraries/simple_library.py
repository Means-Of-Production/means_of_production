from datetime import datetime
from typing import Iterable, List, Optional

from domain.entities.borrower import Borrower
from domain.entities.libraries.base_library import BaseLibrary
from domain.entities.lenders.lender import Lender
from domain.entities.loan import Loan
from domain.entities.people.person import Person
from domain.entities.thing import Thing
from domain.value_items import ID, DueDate, ThingTitle, ThingStatus, LoanStatus, Money, TimeInterval, PhysicalLocation


class SimpleLibrary(BaseLibrary, Lender):
    library_id: ID
    name: str
    administrator: Person
    location: PhysicalLocation
    _items: List[Thing] = []
    
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
    
    async def borrow(self, thing: Thing, borrower: Borrower, until: Optional[DueDate] = None) -> Loan:
        # Check if available
        if thing.status != ThingStatus.READY:
            from domain.value_items.exceptions import InvalidThingStatusToBorrowError
            raise InvalidThingStatusToBorrowError(thing.status)
            
        # Check if borrower in good standing
        if not self.can_borrow(borrower):
            from domain.value_items.exceptions import BorrowerNotInGoodStandingError
            raise BorrowerNotInGoodStandingError()
            
        if not until:
            until = DueDate(self.default_loan_time.from_now())
            
        # Make loan
        loan = Loan(
            loan_id=ID(),
            item=thing,
            borrower=borrower,
            due_date=until,
            status=LoanStatus.BORROWED,
            return_location=self.location,
            date_returned=None
        )
        
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
    
    def preferred_return_location(self, item: Thing) -> PhysicalLocation:
        return self.location
    
    async def start_return(self, loan: Loan) -> Loan:
        # Simple library does not have an acceptance step, only the library starts returns!
        loan.status = LoanStatus.RETURN_STARTED
        loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
        loan.date_returned = datetime.now()
        return loan