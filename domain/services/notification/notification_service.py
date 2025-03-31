from abc import ABC, abstractmethod
from domain.entities.waiting_lists.reservation import Reservation

class NotificationService(ABC):
    """Interface for notification services handling borrower notifications."""
    
    @abstractmethod
    def notify_borrower_reserved_item_available(self, reservation: Reservation) -> None:
        """Notify the borrower that a reserved item is available."""
        pass
