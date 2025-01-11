from enum import Enum


class ReservationStatus(Enum):
    ASSIGNED = "ASSIGNED"
    BORROWER_NOTIFIED = "BORROWER_NOTIFIED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    BORROWED = "BORROWED"
