from pydantic import BaseModel
from typing import TYPE_CHECKING

from domain.entities.borrower import Borrower
from domain.value_items.money import Money


class AuctionBid(BaseModel):
    model_config = {"frozen": True}
    amount_bid: 'Money'
    amount_paid: 'Money'
    made_by: 'Borrower'
    made_for: 'Borrower'

    def __eq__(self, other):
        if not isinstance(other, AuctionBid):
            return False
        return (self.amount_bid == other.amount_bid and
                self.amount_paid == other.amount_paid and
                self.made_by == other.made_by and
                self.made_for == other.made_for)

    def __hash__(self):
        return hash((self.amount_bid, self.amount_paid, self.made_by.entity_id, self.made_for.entity_id))