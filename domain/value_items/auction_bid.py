from pydantic import BaseModel

from domain.value_items.id import ID
from domain.value_items.money import Money


class AuctionBid(BaseModel):
    model_config = {"frozen": True}
    amount_bid: Money
    amount_paid: Money
    made_by_id: ID
    made_for_id: ID

    def __eq__(self, other):
        if not isinstance(other, AuctionBid):
            return False
        return (
            self.amount_bid == other.amount_bid
            and self.amount_paid == other.amount_paid
            and self.made_by_id == other.made_by_id
            and self.made_for_id == other.made_for_id
        )

    def __hash__(self):
        return hash(
            (
                self.amount_bid,
                self.amount_paid,
                self.made_by_id,
                self.made_for_id,
            )
        )
