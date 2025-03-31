from domain.services.bidding.bidding_strategy import BiddingStrategy
from domain.entities import Thing 
from domain.entities.people import Borrower 
from domain.entities.libraries import Library
from domain.value_items import Money
from domain.entities.waiting_lists import AuctionBid

class RegularBiddingStrategy(BiddingStrategy):
    """Simple form of bidding - the bid is the amount put in for yourself or another."""

    async def get_bid_for_cost(
        self, thing: Thing, bidder: Borrower, amount_to_pay: Money, library: Library, beneficiary: Borrower = None
    ) -> AuctionBid:
        if beneficiary is None:
            beneficiary = bidder
        return AuctionBid(amount_to_pay, amount_to_pay, bidder, beneficiary)
