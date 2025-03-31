from abc import ABC, abstractmethod
from typing import Optional, Iterable, Dict, List
from domain.entities.people.borrower import Borrower
from domain.entities.thing import Thing
from domain.entities.loans.loan import Loan
from domain.entities.waiting_lists.waiting_list import WaitingList
from domain.entities.waiting_lists.auctionable_waiting_list import AuctionableWaitingList
from domain.entities.factories.waiting_list_factory import WaitingListFactory
from domain.entities.factories.feeschedules.no_fee_schedule import NoFeeSchedule
from domain.entities.factories.money_factory import MoneyFactory
from domain.services.bidding.bidding_strategy import BiddingStrategy
from domain.value_items.due_date import DueDate
from domain.value_items.fee_status import FeeStatus
from domain.value_items.loan_status import LoanStatus
from domain.value_items.mop_server import MOPServer
from domain.value_items.thing_status import ThingStatus
from domain.value_items.thing_title import ThingTitle
from domain.value_items.time_interval import TimeInterval
from domain.entities.libraries.library_fee import LibraryFee
from domain.value_items.exceptions import (
    InvalidLibraryConfigurationError,
    ReturnNotStartedError,
    EntityNotAssignedIdError
)

class BaseLibrary(ABC):
    """
    Abstract base class representing a library system.
    """

    def __init__(
        self, 
        library_id: str, 
        name: str, 
        administrator: Borrower, 
        max_fines_before_suspension, 
        loans: Iterable[Loan], 
        money_factory: MoneyFactory, 
        mop_server: MOPServer, 
        default_loan_time: Optional[TimeInterval] = None, 
        fee_schedule=None, 
        bidding_strategy: Optional[BiddingStrategy] = None, 
        waiting_list_factory=None, 
        public_url: Optional[str] = None
    ):
        self.id = library_id
        self.name = name
        self._borrowers: List[Borrower] = []
        self.administrator = administrator
        self.waiting_lists_by_item_id: Dict[str, WaitingList] = {}
        self.max_fines_before_suspension = max_fines_before_suspension
        self.money_factory = money_factory
        self.mop_server = mop_server
        self.public_url = public_url
        self.bidding_strategy = bidding_strategy
        self._loans: List[Loan] = list(loans)

        self.fee_schedule = fee_schedule if fee_schedule else NoFeeSchedule(money_factory)
        self.default_loan_time = default_loan_time if default_loan_time else TimeInterval.from_days(14)

        if waiting_list_factory is None:
            waiting_list_factory = WaitingListFactory(bool(bidding_strategy), None, money_factory)
        else:
            if waiting_list_factory.supports_auctions and not self.bidding_strategy:
                raise InvalidLibraryConfigurationError("Waiting list supports auctions but no bidding strategy provided!")
            if not waiting_list_factory.supports_auctions and self.bidding_strategy:
                raise InvalidLibraryConfigurationError("Waiting list does not support auctions but bidding strategy provided!")

        self.waiting_list_factory = waiting_list_factory

    @property
    @abstractmethod
    def location(self):
        """
        Returns the location of the library.
        """
        pass

    @abstractmethod
    def get_all_things(self) -> Iterable[Thing]:
        """
        Retrieves all things (items) in the library.
        """
        pass

    def get_available_things(self) -> Iterable[Thing]:
        """
        Retrieves only available items in the library.
        """
        return (thing for thing in self.get_all_things() if thing.status == ThingStatus.READY)

    @abstractmethod
    async def borrow(self, item: Thing, borrower: Borrower, until: DueDate) -> Loan:
        """
        Handles borrowing an item from the library.
        """
        pass

    @abstractmethod
    async def start_return(self, loan: Loan) -> Loan:
        """
        Initiates the return process for a borrowed item.
        """
        pass

    @property
    def borrowers(self) -> Iterable[Borrower]:
        return self._borrowers

    def add_borrower(self, borrower: Borrower) -> Borrower:
        self._borrowers.append(borrower)
        return borrower

    def can_borrow(self, borrower: Borrower) -> bool:
        if borrower.library.name != self.name:
            return False

        outstanding_fees = [
            fee.amount for fee in borrower.fees if fee.status == FeeStatus.OUTSTANDING
        ]
        total_fees = self.money_factory.total(outstanding_fees)
        return not total_fees.greater_than(self.max_fines_before_suspension)

    async def reserve_item(self, item: Thing, borrower: Borrower) -> WaitingList:
        if not item.id:
            raise EntityNotAssignedIdError("Item must have an assigned ID!")

        waiting_list = self.waiting_lists_by_item_id.get(item.id)
        if not waiting_list:
            waiting_list = self.waiting_list_factory.create_list(item)
            self.waiting_lists_by_item_id[item.id] = waiting_list

        waiting_list.add(borrower)
        return waiting_list

    def get_loans(self) -> Iterable[Loan]:
        return self._loans

    def add_loan(self, loan: Loan):
        self._loans.append(loan)

    def get_titles_from_items(self, items: Iterable[Thing]) -> Iterable[ThingTitle]:
        """
        Extracts unique titles from a list of items.
        """
        titles = []
        for item in items:
            if not any(title.equals(item.title) for title in titles):
                titles.append(item.title)
        return titles

    async def finish_return(self, loan: Loan) -> Loan:
        """
        Completes the return process for a loan.
        """
        if loan.status != LoanStatus.WAITING_ON_LENDER_ACCEPTANCE or not loan.date_returned:
            raise ReturnNotStartedError()

        if loan.item.status == ThingStatus.DAMAGED:
            loan.status = LoanStatus.RETURNED_DAMAGED
        else:
            if loan.due_date.date:
                loan.status = LoanStatus.OVERDUE if loan.date_returned > loan.due_date.date else LoanStatus.RETURNED
            else:
                loan.status = LoanStatus.RETURNED

        fee_amount = None
        if loan.item.status == ThingStatus.DAMAGED:
            fee_amount = self.fee_schedule.fees_for_damaged_item(loan)
        elif loan.status == LoanStatus.OVERDUE:
            fee_amount = self.fee_schedule.fees_for_overdue_item(loan)

        if fee_amount:
            fee = LibraryFee(fee_amount, loan, FeeStatus.OUTSTANDING)
            loan.borrower.apply_fee(fee)

        if not loan.item.id:
            raise EntityNotAssignedIdError("Item must have an assigned ID!")

        if loan.item.id in self.waiting_lists_by_item_id:
            waiting_list = self.waiting_lists_by_item_id.get(loan.item.id)
            if waiting_list:
                waiting_list.reserve_item_for_next_borrower()

        if loan.item.status == ThingStatus.BORROWED:
            loan.item.status = ThingStatus.READY

        return loan

    async def bid_to_skip_to_front_of_list(
        self, item: Thing, bidder: Borrower, amount, borrower: Borrower
    ) -> WaitingList:
        """
        Allows a bidder to place a bid to skip to the front of the waiting list.
        """
        if not self.bidding_strategy:
            raise InvalidLibraryConfigurationError("This library does not support bidding!")

        waiting_list = await self.reserve_item(item, borrower)
        auctionable_list = waiting_list  # Assuming it's an IAuctionableWaitingList

        bid = await self.bidding_strategy.get_bid_for_cost(item, bidder, amount, self, borrower)
        return auctionable_list.add_bid(bid)
