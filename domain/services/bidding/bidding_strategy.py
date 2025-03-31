from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import Thing
from domain.entities.people import Borrower 
from domain.entities.libraries import Library
from domain.value_items import Money
from domain.entities.waiting_lists import AuctionBid

class BiddingStrategy(ABC):
    """
    Takes an amount of money and returns an AuctionBid. Allows us to control how bidding actually works.
    """

    @abstractmethod
    async def get_bid_for_cost(
        self, item: Thing, bidder: Borrower, amount_to_pay: Money, library: Library, beneficiary: Optional[Borrower] = None
    ) -> AuctionBid:
        pass
