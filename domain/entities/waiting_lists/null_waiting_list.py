from __future__ import annotations

from datetime import timedelta
from typing import Self

from domain.entities.borrower import Borrower
from domain.entities.waiting_lists.reservation import Reservation
from domain.entities.waiting_lists.waiting_list import WaitingList


class NullWaitingList(WaitingList):
    """
    A specialized implementation of the WaitingList that effectively acts as a no-op
    or placeholder. This class does not maintain an actual waiting list but provides
    the interface and methods required for compliance with the `WaitingList` abstract
    base class.

    This class can be utilized in libraries where we do not allow waiting lists. It ensures
    that all operations related to the waiting list are safely ignored or return
    default values without disrupting other parts of the system.
    """

    def add(self, borrower: Borrower) -> Self:
        return self

    def find_next_borrower(self) -> Borrower | None:
        return None

    def is_on_list(self, borrower: Borrower) -> bool:
        return False

    def process_reservation_expired(self, reservation: Reservation) -> Self:
        return self

    def cancel(self, borrower: Borrower) -> Self:
        return self

    def get_reservation_time(self) -> timedelta:
        return timedelta(days=0)
