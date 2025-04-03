from __future__ import annotations
from typing import TYPE_CHECKING
from domain.services.bidding.bidding_strategy import BiddingStrategy
from domain.value_items import Money, DueDate

if TYPE_CHECKING:
    from domain.entities.loans import Loan
    from domain.entities import Thing
    from domain.entities.people import Borrower
    from domain.entities.libraries import Library
    from domain.entities.waiting_lists import AuctionBid
    from domain.repositories.loan_repository import LoanRepository

class QuadraticBiddingStrategy(BiddingStrategy):
    """
    Form of bidding where the value of a bid decreases the longer it has been held by the same person.
    """

    def __init__(self, loan_repository: 'LoanRepository'):
        self.loan_repository = loan_repository

    @staticmethod
    def compare_loans(a: 'Loan', b: 'Loan') -> int:
        return DueDate.compare(a.due_date, b.due_date)

    async def get_bid_for_cost(
        self, 
        item: 'Thing', 
        bidder: 'Borrower', 
        amount_to_pay: Money, 
        library: 'Library', 
        beneficiary: 'Borrower' = None
    ) -> 'AuctionBid':
        if beneficiary is None:
            beneficiary = bidder

        # Get loans for the item
        item_loans = sorted(
            filter(lambda l: l.item.id == item.id, await self.loan_repository.get_loans_for_library(library)),
            key=lambda l: l.due_date
        )

        # Count how many times the beneficiary has consecutively held this item
        num_previous_loans = 0
        for loan in item_loans:
            if loan.borrower.id == beneficiary.id:
                num_previous_loans += 1
            else:
                break

        # The longer you hold the item, the less you can bid
        amount_bid = amount_to_pay.multiply(1 / num_previous_loans) if num_previous_loans > 0 else amount_to_pay

        return AuctionBid(amount_bid, amount_to_pay, bidder, beneficiary)