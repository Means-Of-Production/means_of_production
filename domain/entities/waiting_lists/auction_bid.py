from dataclasses import dataclass
from domain.entities.people.borrower import Borrower
from domain.value_items.money import Money


@dataclass(frozen=True)
class AuctionBid:
    """Represents an auction bid made by a borrower for another borrower."""
    made_by: Borrower
    made_for: Borrower
    amount_paid: Money  # Paid and bid amounts can differ (e.g., for quadratic bidding)
    amount_bid: Money
