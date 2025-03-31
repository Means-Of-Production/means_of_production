from typing import List, Optional
from domain.entities.waiting_lists.base_waiting_list import BaseWaitingList
from domain.entities.people.borrower import Borrower
from domain.entities.thing import Thing
from domain.value_items.time_interval import TimeInterval
from domain.entities.waiting_lists.reservation import Reservation
from domain.value_items.reservation_status import ReservationStatus


class FirstComeFirstServeWaitingList(BaseWaitingList):
    """
    Implements a first-come-first-serve waiting list for an item.
    """

    def __init__(self, item: Thing, members: Optional[List[Borrower]] = None, reservation_days: int = 3):
        super().__init__(item)
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
        member_ids = [b.id for b in self.members]
        return borrower.id is not None and borrower.id in member_ids

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

    def process_reservation_expired(self, reservation: Reservation) -> "FirstComeFirstServeWaitingList":
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
