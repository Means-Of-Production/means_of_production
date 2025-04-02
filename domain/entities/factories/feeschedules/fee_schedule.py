from abc import ABC, abstractmethod
from domain.entities.loans.loan import Loan
from domain.value_items.money import Money


class FeeSchedule(ABC):
    """Abstract Base Class for Fee Schedules"""

    @abstractmethod
    def fees_for_overdue_item(self, loan: Loan) -> Money:
        """Calculates fees for an overdue item"""
        pass

    @abstractmethod
    def fees_for_damaged_item(self, loan: Loan) -> Money:
        """Calculates fees for a damaged item"""
        pass


class StandardFeeSchedule(FeeSchedule):
    """Concrete Implementation of FeeSchedule"""

    def fees_for_overdue_item(self, loan: Loan) -> Money:
        return Money(amount=5.00, currency="USD")  # Example fee

    def fees_for_damaged_item(self, loan: Loan) -> Money:
        return Money(amount=20.00, currency="USD")  # Example fee
