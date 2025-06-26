from datetime import datetime

from domain.entities.borrower import Borrower
from domain.entities.entity import Entity
from domain.entities.thing import Thing
from domain.value_items import ID, ReservationStatus


class Reservation(Entity):
    model_config = {"frozen": False}
    reservation_id: ID
    holder: Borrower
    item: Thing
    good_until: datetime
    _status: ReservationStatus

    @property
    def entity_id(self) -> ID:
        return self.reservation_id

    @property
    def status(self) -> ReservationStatus:
        return self._status

    @status.setter
    def status(self, status: ReservationStatus) -> None:
        valid_next_status = []

        if self.status == ReservationStatus.ASSIGNED:
            valid_next_status = [ReservationStatus.BORROWER_NOTIFIED]
        elif self.status == ReservationStatus.BORROWER_NOTIFIED:
            valid_next_status = [ReservationStatus.EXPIRED, ReservationStatus.BORROWED]
        elif self.status == ReservationStatus.BORROWED:
            valid_next_status = []
        elif self.status == ReservationStatus.EXPIRED:
            valid_next_status = []
        elif self.status == ReservationStatus.CANCELLED:
            valid_next_status = []

        if status not in valid_next_status:
            from domain.value_items.exceptions import (
                InvalidReservationStateTransitionError,
            )

            raise InvalidReservationStateTransitionError(self.status, status)

        self._status = status
