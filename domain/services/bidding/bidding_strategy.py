from abc import ABC, abstractmethod
from domain.entities.thing import Thing
from domain.entities.people.borrower import Borrower
from domain.value_items.money import Money
from domain.entities.waiting_lists.auction_bid import AuctionBid
from domain.entities.libraries.library import Library


class BiddingStrategy(ABC):
    """
    Takes an amount of money and returns an AuctionBid. Allows us to control how bidding actually works.
    """

    @abstractmethod
    async def get_bid_for_cost(
        self,
        item: Thing,
        bidder: Borrower,
        amount_to_pay: Money,
        library: "Library",
        beneficiary: Borrower | None = None,
    ) -> AuctionBid:
        pass
