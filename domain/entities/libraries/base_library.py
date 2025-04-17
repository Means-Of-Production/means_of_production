from typing import Iterable, Optional, Dict, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from domain.entities import (
    Thing,
    Borrower,
    Person,
    Loan,
    FeeSchedule,
    WaitingListFactory,
    MoneyFactory,
    NoFeeSchedule,
    WaitingList,
)
from domain.value_items import (
    DueDate,
    FeeStatus,
    Location,
    Money,
    LoanStatus,
    MOPServer,
    ThingStatus,
    ThingTitle,
    TimeInterval,
)
from domain.services import BiddingStrategy


class EntityNotAssignedIdError(Exception):
    pass


class InvalidLibraryConfigurationError(Exception):
    pass


class ReturnNotStartedError(Exception):
    pass


@dataclass
class URL:
    """Simple URL representation"""

    url: str


class LibraryFee:
    def __init__(self, amount: Money, loan: Loan, status: FeeStatus):
        self.amount = amount
        self.loan = loan
        self.status = status


class BaseLibrary(ABC):
    def __init__(
        self,
        id: str,
        name: str,
        administrator: Person,
        max_fines_before_suspension: Money,
        loans: Iterable[Loan],
        money_factory: MoneyFactory,
        mop_server: MOPServer,
        default_loan_time: Optional[TimeInterval] = None,
        fee_schedule: Optional[FeeSchedule] = None,
        bidding_strategy: Optional[BiddingStrategy] = None,
        waiting_list_factory: Optional[WaitingListFactory] = None,
        public_url: Optional[URL] = None,
    ):
        self._borrowers: List[Borrower] = []
        self._loans: List[Loan] = list(loans)
        self.name = name
        self.id = id
        self.waiting_list_factory = waiting_list_factory or WaitingListFactory(
            bidding_strategy is not None, None, money_factory
        )
        self.waiting_lists_by_item_id: Dict[str, WaitingList] = {}
        self.administrator = administrator
        self.max_fines_before_suspension = max_fines_before_suspension
        self.fee_schedule = fee_schedule or NoFeeSchedule(money_factory)
        self.money_factory = money_factory
        self.default_loan_time = default_loan_time or TimeInterval.from_days(14)
        self.mop_server = mop_server
        self.public_url = public_url
        self.bidding_strategy = bidding_strategy

        if waiting_list_factory:
            if waiting_list_factory.supports_auctions and not self.bidding_strategy:
                raise InvalidLibraryConfigurationError(
                    "Waiting list supports auctions but no bidding strategy provided!"
                )
            if not waiting_list_factory.supports_auctions and self.bidding_strategy:
                raise InvalidLibraryConfigurationError(
                    "Waiting list does not support auctions but bidding strategy provided!"
                )

    @property
    @abstractmethod
    def location(self) -> Location:
        pass

    @abstractmethod
    def get_all_things(self) -> Iterable[Thing]:
        pass

    def get_available_things(self) -> Iterable[Thing]:
        for thing in self.get_all_things():
            if thing.status == ThingStatus.READY:
                yield thing

    @abstractmethod
    async def borrow(self, item: Thing, borrower: Borrower, until: DueDate) -> Loan:
        pass

    @abstractmethod
    async def start_return(self, loan: Loan) -> Loan:
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

        fee_amounts = [
            f.amount for f in borrower.fees if f.status == FeeStatus.OUTSTANDING
        ]
        total_fees = self.money_factory.total(fee_amounts)
        return not total_fees.greater_than(self.max_fines_before_suspension)

    async def reserve_item(self, item: Thing, borrower: Borrower) -> WaitingList:
        if not item.id:
            raise EntityNotAssignedIdError("Item must have an ID")

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

    def _get_titles_from_items(self, items: Iterable[Thing]) -> Iterable[ThingTitle]:
        titles = []
        for item in items:
            existing = [t for t in titles if t.equals(item.title)]
            if not existing:
                titles.append(item.title)
        return titles

    async def finish_return(self, loan: Loan) -> Loan:
        if (
            loan.status != LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
            or not loan.date_returned
        ):
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
            raise EntityNotAssignedIdError("Item must have an ID")

        if loan.item.id in self.waiting_lists_by_item_id:
            waiting_list = self.waiting_lists_by_item_id[loan.item.id]
            waiting_list.reserve_item_for_next_borrower()

        if loan.item.status == ThingStatus.BORROWED:
            loan.item.status = ThingStatus.READY

        return loan

    async def bid_to_skip_to_front_of_list(
        self, item: Thing, bidder: Borrower, amount: Money, borrower: Borrower
    ) -> WaitingList:
        if not self.bidding_strategy:
            raise InvalidLibraryConfigurationError(
                "This library does not support bidding!"
            )

        waiting_list = await self.reserve_item(item, borrower)
        auctionable_list = waiting_list  # type: AuctionableWaitingList

        bid = await self.bidding_strategy.get_bid_for_cost(
            item, bidder, amount, self, borrower
        )
        return auctionable_list.add_bid(bid)
