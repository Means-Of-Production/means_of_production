from __future__ import annotations

from datetime import timedelta
from typing import Self

from domain.entities.borrower import Borrower
from domain.entities.thing import Thing
from domain.entities.waiting_lists.base_waiting_list import BaseWaitingList
from domain.entities.waiting_lists.reservation import Reservation
from domain.value_items import ID, ReservationStatus


class FirstComeFirstServeWaitingList(BaseWaitingList):
    waiting_list_id: ID
    _item: Thing
    members: list[Borrower] = []
    reservation_days: int = 3

    @property
    def entity_id(self) -> ID:
        return self.waiting_list_id

    def add(self, borrower: Borrower) -> Self:
        self.members.append(borrower)
        return self

    def is_on_list(self, borrower: Borrower) -> bool:
        member_ids = [b.entity_id for b in self.members]
        return borrower.entity_id is not None and borrower.entity_id in member_ids

    def find_next_borrower(self) -> Borrower | None:
        if not self.members:
            return None
        return self.members[0]

    def get_reservation_time(self) -> timedelta:
        return timedelta(days=self.reservation_days)

    def process_reservation_expired(self, reservation: Reservation) -> Self:
        reservation.status = ReservationStatus.EXPIRED
        self._expired_reservations.append(reservation)
        self.clear_current_reservation()

        return self

    def cancel(self, borrower: Borrower) -> Self:
        self.members = [b for b in self.members if b.entity_id != borrower.entity_id]

        return self
