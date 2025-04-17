from domain.value_items.reservation_status import ReservationStatus
from domain.value_items.thing_status import ThingStatus


class CurrencyMismatchException(Exception):
    """Raised when a currency mismatch occurs."""

    pass


class InvalidThingStateTransitionError(Exception):
    """Raised when an invalid transition occurs in ThingStatus."""

    def __init__(self, current_status: ThingStatus, new_status: ThingStatus):
        self.current_status = current_status
        self.new_status = new_status
        message = (
            f"Invalid thing state transition. Current status: {current_status}, "
            f"New status: {new_status}"
        )
        super().__init__(message)


class InvalidReservationStateTransitionError(Exception):
    """Raised when an invalid transition occurs in ReservationStatus."""

    def __init__(
        self, current_status: ReservationStatus, new_status: ReservationStatus
    ):
        self.current_status = current_status
        self.new_status = new_status
        message = (
            f"Invalid reservation state transition. Current status: {current_status}, "
            f"New status: {new_status}"
        )
        super().__init__(message)


class ReturnNotStartedError(Exception):
    """Raised when an attempt is made to return an item before starting the return process."""

    def __init__(self, message="Return process has not been started yet."):
        super().__init__(message)


class InvalidLibraryConfigurationError(Exception):
    """Raised when the library configuration is invalid."""

    def __init__(self, message="Invalid library configuration."):
        super().__init__(message)


class EntityNotAssignedIdError(Exception):
    """Raised when an entity does not have an assigned ID."""

    def __init__(self, message="Entity does not have an assigned ID."):
        super().__init__(message)


class ConflictingKeyException(Exception):
    """Raised when there is a conflicting key issue."""

    pass


class ResourceNotFoundException(Exception):
    """Raised when a requested resource is not found."""

    pass


class InvalidThingStatusToBorrowError(Exception):
    """Raised when attempting to borrow an item with an invalid status."""

    def __init__(self, status: ThingStatus):
        self.status = status
        message = f"Attempting to borrow a thing with status of {status}"
        super().__init__(message)


class BorrowerNotInGoodStandingError(Exception):
    """Raised when a borrower is not in good standing."""

    pass
