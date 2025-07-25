from datetime import datetime
from pydantic import PrivateAttr

from domain.entities.borrower import Borrower
from domain.entities.entity import Entity
from domain.entities.thing import Thing
from domain.value_items import ID, ReservationStatus
from domain.value_items.exceptions import InvalidReservationStateTransitionError


class Reservation(Entity):
    model_config = {"frozen": False}

    reservation_id: ID
    holder: Borrower
    item: Thing
    good_until: datetime

    _status: ReservationStatus = PrivateAttr(default=ReservationStatus.ASSIGNED)

    @property
    def status(self) -> ReservationStatus:
        """Access the reservation status."""
        return self._status

    @status.setter
    def status(self, new_status: ReservationStatus) -> None:
        """Set reservation status with validation on allowed transitions."""
        valid_next_status = []

        if self._status == ReservationStatus.ASSIGNED:
            valid_next_status = [
                ReservationStatus.BORROWER_NOTIFIED,
                ReservationStatus.CANCELLED,
            ]
        elif self._status == ReservationStatus.BORROWER_NOTIFIED:
            valid_next_status = [
                ReservationStatus.BORROWED,
                ReservationStatus.EXPIRED,
                ReservationStatus.CANCELLED,
            ]
        elif self._status in {
            ReservationStatus.BORROWED,
            ReservationStatus.EXPIRED,
            ReservationStatus.CANCELLED,
        }:
            valid_next_status = []

        if new_status not in valid_next_status:
            raise InvalidReservationStateTransitionError(self._status, new_status)

        self._status = new_status

    @property
    def entity_id(self) -> ID:
        return self.reservation_id
