from pydantic import BaseModel, field_validator
from domain.entities.people.borrower import Borrower
from domain.value_items.money import Money


class AuctionBid(BaseModel):
    """
    Represents an auction bid made by a borrower for another borrower.
    Uses Pydantic for validation and serialization.
    """

    made_by: Borrower
    made_for: Borrower
    amount_paid: Money  # Paid and bid amounts can differ (e.g., for quadratic bidding)
    amount_bid: Money

    @field_validator("amount_paid", "amount_bid")
    @classmethod
    def validate_positive_amount(cls, value: Money) -> Money:
        """Ensure bid amounts are positive"""
        if value.amount <= 0:
            raise ValueError("Bid amounts must be positive")
        return value

    class Config:
        frozen = True  # Makes the model immutable
        arbitrary_types_allowed = True  # Allows custom types like Money
