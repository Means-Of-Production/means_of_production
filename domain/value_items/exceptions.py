from domain.value_items.reservation_status import ReservationStatus
from domain.value_items.thing_status import ThingStatus


class CurrencyMismatchException(Exception):
    pass


class InvalidThingStateTransitionError(Exception):
    def __init__(self, current_status: ThingStatus, new_status: ThingStatus):
        self.current_status = current_status
        self.new_status = new_status

        message = f"Invalid thing state transition. Current status: {current_status}, New status: {new_status}"
        super().__init__(message)


class InvalidReservationStateTransitionError(Exception):
    def __init__(
        self, current_status: ReservationStatus, new_status: ReservationStatus
    ):
        self.current_status = current_status
        self.new_status = new_status

        message = f"Invalid reservation state transition. Current status: {current_status}, New status: {new_status}"
        super().__init__(message)


class ReturnNotStartedError(Exception):
    pass
