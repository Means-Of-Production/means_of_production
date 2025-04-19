from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Iterable, List, Optional, Dict

from domain.entities.borrower import Borrower
from domain.entities.libraries.library import Library
from domain.entities.libraries.library_fee import LibraryFee
from domain.entities.loan import Loan
from domain.entities.people.person import Person
from domain.entities.thing import Thing
from domain.entities.waiting_lists.base_waiting_list import BaseWaitingList
from domain.value_items import ID, DueDate, Location, ThingTitle, ThingStatus, LoanStatus, FeeStatus, Money


class BaseLibrary(Library, ABC):
    library_id: ID
    name: str
    administrator: Person
    location: Location
    _borrowers: List[Borrower] = []
    _loans: List[Loan] = []
    waiting_list_factory: 'WaitingListFactory'  # Forward reference
    waiting_lists_by_item_id: Dict[str, BaseWaitingList] = {}
    max_fines_before_suspension: Money
    fee_schedule: 'FeeSchedule'  # Forward reference
    money_factory: 'MoneyFactory'  # Forward reference
    default_loan_time: timedelta 
    bidding_strategy: BiddingStrategy | None = None  # Forward reference
    mop_server: 'MOPServer'  # Forward reference
    public_url: Optional[str] = None
    
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
    def borrow(self, thing: Thing, borrower: Borrower, until: DueDate) -> Loan:
        pass
    
    @abstractmethod
    def start_return(self, loan: Loan) -> Loan:
        pass
    
    @property
    def borrowers(self) -> Iterable[Borrower]:
        return self._borrowers
    
    def add_borrower(self, borrower: Borrower) -> Borrower:
        self._borrowers.append(borrower)
        return borrower
    
    def can_borrow(self, borrower: Borrower) -> bool:
        if borrower.library.entity_id != self.entity_id:
            return False
        
        fee_amounts = [f.amount for f in borrower.fees if f.status == FeeStatus.OUTSTANDING]
        total_fees = self.money_factory.total(fee_amounts)
        return not total_fees.greater_than(self.max_fines_before_suspension)
    
    async def reserve_item(self, item: Thing, borrower: Borrower) -> BaseWaitingList:
        if not item.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError
            raise EntityNotAssignedIdError("")
            
        waiting_list = self.waiting_lists_by_item_id.get(item.entity_id.value)
        if not waiting_list:
            waiting_list = self.waiting_list_factory.create_list(item)
            self.waiting_lists_by_item_id[item.entity_id.value] = waiting_list
            
        waiting_list.add(borrower)
        return waiting_list
    
    def get_loans(self) -> Iterable[Loan]:
        return self._loans
    
    def add_loan(self, loan: Loan) -> None:
        self._loans.append(loan)
    
    def get_titles_from_items(self, items: Iterable[Thing]) -> Iterable[ThingTitle]:
        titles = []
        for item in items:
            if not any(t == item.title for t in titles):
                titles.append(item.title)
        return titles
    
    async def finish_return(self, loan: Loan) -> Loan:
        # This has to call FIRST, so the status can be updated to act here
        if loan.status != LoanStatus.WAITING_ON_LENDER_ACCEPTANCE or not loan.date_returned:
            from domain.value_items.exceptions import ReturnNotStartedError
            raise ReturnNotStartedError()
            
        if loan.item.status == ThingStatus.DAMAGED:
            loan.status = LoanStatus.RETURNED_DAMAGED
        else:
            if loan.due_date.date:
                if loan.date_returned > loan.due_date.date:
                    loan.status = LoanStatus.OVERDUE
                else:
                    loan.status = LoanStatus.RETURNED
            else:
                # Should we be able to return things without a date?
                loan.status = LoanStatus.RETURNED
                
        fee_amount = None
        if loan.item.status == ThingStatus.DAMAGED:
            # Apply the fees
            fee_amount = self.fee_schedule.fees_for_damaged_item(loan)
            
        if loan.status == LoanStatus.OVERDUE:
            # Calculate the late fee and apply
            fee_amount = self.fee_schedule.fees_for_overdue_item(loan)
            
        if fee_amount:
            fee = LibraryFee(
                library_fee_id=ID(),
                library_id=self.library_id,
                amount=fee_amount,
                charged_for=loan,
                status=FeeStatus.OUTSTANDING
            )
            loan.borrower.apply_fee(fee)
            
        # Is there a waiting list for the item?
        if not loan.item.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError
            raise EntityNotAssignedIdError("")
            
        if loan.item.entity_id.value in self.waiting_lists_by_item_id:
            waiting_list = self.waiting_lists_by_item_id[loan.item.entity_id.value]
            if waiting_list:
                waiting_list.reserve_item_for_next_borrower()
                
        if loan.item.status == ThingStatus.BORROWED:
            loan.item.status = ThingStatus.READY
            
        return loan
    
    async def bid_to_skip_to_front_of_list(self, item: Thing, bidder: Borrower, amount: Money, borrower: Borrower) -> BaseWaitingList:
        if not self.bidding_strategy:
            from domain.value_items.exceptions import InvalidLibraryConfigurationError
            raise InvalidLibraryConfigurationError("This library does not support bidding!")
            
        waiting_list = await self.reserve_item(item, borrower)
        from domain.entities.waiting_lists.auctionable_waiting_list import AuctionableWaitingList
        auctionable_list = waiting_list  # Type assertion
        
        bid = await self.bidding_strategy.get_bid_for_cost(item, bidder, amount, self, borrower)
        return auctionable_list.add_bid(bid)