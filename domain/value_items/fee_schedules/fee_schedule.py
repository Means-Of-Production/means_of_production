from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from domain.value_items.money import Money


class FeeSchedule(ABC, BaseModel):
    @abstractmethod
    def fee_for_overdue_item(self, loan) -> Money:
        raise NotImplementedError()

    def fee_for_damaged_item(self, loan) -> Money:
        raise NotImplementedError()
