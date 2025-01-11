from datetime import datetime

from pydantic import PrivateAttr, computed_field

from domain.entities.borrower import Borrower
from domain.entities.entity import Entity
from domain.value_items import ID, ReservationStatus, ThingTitle
from domain.value_items.exceptions import InvalidReservationStateTransitionError


class Reservation(Entity):
    reservation_id: ID
    holder: Borrower
    item: ThingTitle
    good_until: datetime
    _status: ReservationStatus = PrivateAttr()

    @property
    def entity_id(self) -> ID:
        return self.reservation_id

    @computed_field
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        valid_next_status = []
        match self._status:
            case ReservationStatus.ASSIGNED:
                valid_next_status = [ReservationStatus.BORROWER_NOTIFIED]
            case ReservationStatus.BORROWER_NOTIFIED:
                valid_next_status = [
                    ReservationStatus.EXPIRED,
                    ReservationStatus.BORROWED,
                ]
            case ReservationStatus.BORROWED:
                valid_next_status = []
            case ReservationStatus.EXPIRED:
                valid_next_status = []
            case ReservationStatus.CANCELLED:
                valid_next_status = []

        if value not in valid_next_status:
            raise InvalidReservationStateTransitionError(self._status, value)

        self._status = ReservationStatus(value)
