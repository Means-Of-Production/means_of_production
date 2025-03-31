from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.waiting_lists.reservation import Reservation
from domain.entities.people.borrower import Borrower
from domain.entities.thing import Thing
from domain.value_items.time_interval import TimeInterval
from domain.value_items.thing_status import ThingStatus
from domain.value_items.reservation_status import ReservationStatus


class BaseWaitingList(ABC):
    """
    Abstract base class for waiting lists.
    """

    def __init__(self, item: Thing, current_reservation: Optional[Reservation] = None, expired_reservations: Optional[List[Reservation]] = None):
        self._item = item
        self._current_reservation = current_reservation
        self._expired_reservations = expired_reservations if expired_reservations is not None else []

    @abstractmethod
    def add(self, borrower: Borrower) -> "BaseWaitingList":
        """
        Adds a borrower to the waiting list.
        """
        pass

    @abstractmethod
    def find_next_borrower(self) -> Optional[Borrower]:
        """
        Finds the next borrower in line.
        """
        pass

    @abstractmethod
    def is_on_list(self, borrower: Borrower) -> bool:
        """
        Checks if a borrower is on the waiting list.
        """
        pass

    @abstractmethod
    def process_reservation_expired(self, reservation: Reservation) -> "BaseWaitingList":
        """
        Handles an expired reservation.
        """
        pass

    @abstractmethod
    def cancel(self, borrower: Borrower) -> "BaseWaitingList":
        """
        Cancels a borrower's place in the waiting list.
        """
        pass

    @abstractmethod
    def _get_reservation_time(self) -> TimeInterval:
        """
        Returns the time interval for a reservation.
        """
        pass

    @property
    def item(self) -> Thing:
        return self._item

    @property
    def current_reservation(self) -> Optional[Reservation]:
        return self._current_reservation

    def _clear_current_reservation(self):
        self._current_reservation = None

    def reserve_item_for_next_borrower(self) -> Reservation:
        """
        Reserves the item for the next borrower in the list.
        """
        if self.current_reservation:
            raise ValueError("This item already has a reservation, please remove that first.")

        next_borrower = self.find_next_borrower()
        if not next_borrower:
            raise ValueError("No borrower is waiting for this item!")

        good_until = self._get_reservation_time().from_now()

        # Change item status
        self.item.status = ThingStatus.RESERVED

        res = Reservation(None, next_borrower, self.item, good_until, ReservationStatus.ASSIGNED)
        self.cancel(next_borrower)
        self._current_reservation = res

        return res
