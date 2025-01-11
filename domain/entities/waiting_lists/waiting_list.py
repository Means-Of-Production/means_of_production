from __future__ import annotations

from abc import abstractmethod
from datetime import timedelta
from typing import Self

from pydantic import PrivateAttr, computed_field

from domain.entities.entity import Entity
from domain.entities.people.borrower import Borrower
from domain.entities.thing import Thing
from domain.entities.waiting_lists.reservation import Reservation
from domain.value_items import ThingTitle


class WaitingList(Entity):
    _item: Thing = PrivateAttr()
    model_config = {"frozen": True}
    _current_reservation: Reservation | None = PrivateAttr(default=None)
    _expired_reservation: list[Reservation] = PrivateAttr(default_factory=list)

    @abstractmethod
    def add(self, borrower: Borrower) -> Self:
        raise NotImplementedError()

    @abstractmethod
    def find_next_borrower(self) -> Borrower | None:
        raise NotImplementedError()

    @abstractmethod
    def is_on_list(self, borrower: Borrower) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def process_reservation_expired(self, reservation: Reservation) -> WaitingList:
        raise NotImplementedError()

    @abstractmethod
    def cancel(self, borrower: Borrower) -> Self:
        raise NotImplementedError()

    @abstractmethod
    def get_reservation_time(self) -> timedelta:
        raise NotImplementedError()

    @computed_field
    @property
    def title(self) -> ThingTitle:
        return self._item.title

    @computed_field
    @property
    def current_reservation(self) -> Reservation | None:
        return self._current_reservation

    def clear_current_reservation(self) -> Self:
        self._current_reservation = None
        return self

    def reserve_item_for_next_borrower(self, thing: Thing) -> Reservation:
        # todo figure out how to reserve a title but deliver a thing!
        raise NotImplementedError()
