from __future__ import annotations

from abc import abstractmethod
from datetime import UTC, datetime, timedelta

from domain.entities.borrower import Borrower
from domain.entities.entity import Entity
from domain.entities.thing import Thing
from domain.entities.waiting_lists.reservation import Reservation
from domain.value_items import ID, ReservationStatus, ThingStatus


class BaseWaitingList(Entity):
    waiting_list_id: ID
    _item: Thing
    _current_reservation: Reservation | None = None
    _expired_reservations: list[Reservation] = []

    @property
    def entity_id(self) -> ID:
        return self.waiting_list_id

    @abstractmethod
    def add(self, borrower: Borrower) -> "BaseWaitingList":
        pass

    @abstractmethod
    def find_next_borrower(self) -> Borrower | None:
        pass

    @abstractmethod
    def is_on_list(self, borrower: Borrower) -> bool:
        pass

    @abstractmethod
    def process_reservation_expired(self, reservation: Reservation) -> BaseWaitingList:
        pass

    @abstractmethod
    def cancel(self, borrower: Borrower) -> "BaseWaitingList":
        pass

    @abstractmethod
    def get_reservation_time(self) -> timedelta:
        pass

    @property
    def item(self) -> Thing:
        return self._item

    @property
    def current_reservation(self) -> Reservation | None:
        return self._current_reservation

    def clear_current_reservation(self) -> None:
        self._current_reservation = None

    def reserve_item_for_next_borrower(self) -> Reservation:
        if self.current_reservation:
            raise ValueError(
                "This item already has a reservation, please remove that first"
            )

        next_borrower = self.find_next_borrower()
        if not next_borrower:
            raise ValueError("No borrower is waiting for this item!")

        good_until = datetime.now(UTC) + self.get_reservation_time()

        # Change item status
        self.item.status = ThingStatus.RESERVED

        res = Reservation(
            reservation_id=ID.generate(),
            holder=next_borrower,
            item=self.item,
            good_until=good_until,
            _status=ReservationStatus.ASSIGNED,
        )

        self.cancel(next_borrower)
        self._current_reservation = res

        return res
