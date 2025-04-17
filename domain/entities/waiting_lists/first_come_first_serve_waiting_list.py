from typing import Optional

# In other files, now you can import cleanly:
from domain.entities.waiting_lists import (
    WaitingList,
    Reservation,
)
from domain.entities.thing import Thing
from domain.entities.people import Borrower
from domain.value_items import TimeInterval, ReservationStatus


class FirstComeFirstServeWaitingList(WaitingList):
    """
    Implements a first-come-first-serve waiting list for an item.
    """

    def __init__(
        self,
        item: Thing,
        members: list[Borrower] | None = None,
        reservation_days: int = 3,
    ):
        super().__init__([item])
        self.members = members if members is not None else []
        self.reservation_days = reservation_days

    def add(self, borrower: Borrower) -> "FirstComeFirstServeWaitingList":
        """
        Adds a borrower to the waiting list.
        """
        self.members.append(borrower)
        return self

    def is_on_list(self, borrower: Borrower) -> bool:
        """
        Checks if a borrower is on the waiting list.
        """
        member_ids = [b.entity_id for b in self.members]
        return borrower.entity_id is not None and borrower.entity_id in member_ids

    def find_next_borrower(self) -> Optional[Borrower]:
        """
        Finds the next borrower in line.
        """
        return self.members[0] if self.members else None

    def _get_reservation_time(self) -> TimeInterval:
        """
        Returns the time interval for a reservation.
        """
        return TimeInterval.from_days(self.reservation_days)

    def process_reservation_expired(
        self, reservation: Reservation
    ) -> "FirstComeFirstServeWaitingList":
        """
        Handles an expired reservation.
        """
        reservation.status = ReservationStatus.EXPIRED
        self._expired_reservations.append(reservation)
        self.clear_current_reservation()

        return self

    def cancel(self, borrower: Borrower) -> "FirstComeFirstServeWaitingList":
        """
        Cancels a borrower's place in the waiting list.
        """
        self.members = [b for b in self.members if b.id != borrower.id]
        return self
