from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.loan import Loan
from domain.value_items.money import Money


class BaseFeeSchedule(ABC):
    @abstractmethod
    def fee_for_overdue_item(self, loan: Loan) -> Money:
        raise NotImplementedError()

    def fee_for_damaged_item(self, loan: Loan) -> Money:
        raise NotImplementedError()
