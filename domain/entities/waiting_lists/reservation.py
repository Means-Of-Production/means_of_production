from datetime import datetime

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
    status: ReservationStatus = ReservationStatus.ASSIGNED

    @property
    def entity_id(self) -> ID:
        return self.reservation_id

    def transition_to(self, new_status: ReservationStatus) -> None:
        valid_next_status = []

        if self.status == ReservationStatus.ASSIGNED:
            valid_next_status = [
                ReservationStatus.BORROWER_NOTIFIED,
                ReservationStatus.CANCELLED,
            ]
        elif self.status == ReservationStatus.BORROWER_NOTIFIED:
            valid_next_status = [
                ReservationStatus.BORROWED,
                ReservationStatus.EXPIRED,
                ReservationStatus.CANCELLED,
            ]
        elif self.status == ReservationStatus.BORROWED:
            valid_next_status = []
        elif self.status == ReservationStatus.EXPIRED:
            valid_next_status = []
        elif self.status == ReservationStatus.CANCELLED:
            valid_next_status = []

        if new_status not in valid_next_status:
            raise InvalidReservationStateTransitionError(self.status, new_status)

        self.status = new_status
