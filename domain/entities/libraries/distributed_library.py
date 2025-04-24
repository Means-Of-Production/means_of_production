from datetime import datetime
from typing import Iterable, List, Optional

from domain.entities.borrower import Borrower
from domain.entities.lenders.lender import Lender
from domain.entities.libraries.library import BaseLibrary
from domain.entities.loan import Loan
from domain.entities.people.person import Person
from domain.entities.thing import Thing
from domain.value_items import ID, DueDate, Location, PhysicalArea, ThingStatus, LoanStatus


class DistributedLibrary(BaseLibrary):
    library_id: ID
    name: str
    administrator: Person
    location: PhysicalArea
    _lenders: List[Lender] = []
    
    @property
    def entity_id(self) -> ID:
        return self.library_id
    
    @property
    def all_things(self) -> Iterable[Thing]:
        for lender in self._lenders:
            for thing in lender.items:
                yield thing
    
    def get_owner_of_item(self, item: Thing) -> Lender:
        for lender in self._lenders:
            for lender_item in lender.items:
                if item.entity_id == lender_item.entity_id:
                    return lender
        raise ValueError(f"Cannot find an owner for {item.title.name}")
    
    async def borrow(self, thing: Thing, borrower: Borrower, until: Optional[DueDate] = None) -> Loan:
        if thing.status != ThingStatus.READY:
            from domain.value_items.exceptions import InvalidThingStatusToBorrowError
            raise InvalidThingStatusToBorrowError(thing.status)
            
        # Check if borrower in good standing
        if not self.can_borrow(borrower):
            from domain.value_items.exceptions import BorrowerNotInGoodStandingError
            raise BorrowerNotInGoodStandingError()
            
        # Get the lender for this item
        lender = self.get_owner_of_item(thing)
        if not lender:
            raise ValueError(f"Cannot find owner of item {thing.entity_id}")
            
        if not until:
            until = DueDate(self.default_loan_time.from_now())
            
        thing.status = ThingStatus.BORROWED
        
        return Loan(
            loan_id=ID(),
            item=thing,
            borrower=borrower,
            due_date=until,
            status=LoanStatus.BORROWED,
            return_location=lender.preferred_return_location(thing),
            date_returned=None
        )
    
    async def finish_return(self, loan: Loan) -> Loan:
        owner = self.get_owner_of_item(loan.item)
        from_owner = await owner.finish_return(loan)
        return await super().finish_return(from_owner)
    
    async def start_return(self, loan: Loan) -> Loan:
        # TODO check the borrower is somewhere near where they should be!
        owner = self.get_owner_of_item(loan.item)
        updated = await owner.start_return(loan)
        
        loan.date_returned = datetime.now()
        # TODO notify the owner that we have started the return
        
        loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
        return updated
    
    def add_lender(self, lender: Lender) -> Lender:
        self._lenders.append(lender)
        return lender