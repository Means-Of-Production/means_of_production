from __future__ import annotations  # Enables forward references
from abc import abstractmethod
from typing import Iterable, TYPE_CHECKING
from domain.entities.entity import Entity

if TYPE_CHECKING:
    from domain.entities.thing import Thing
    from domain.entities.loans.loan import Loan


class Lender(Entity):
    @property
    @abstractmethod
    def items(self) -> Iterable[Thing]:
        raise NotImplementedError()

    @abstractmethod
    def start_return(self, loan: Loan) -> Loan:
        raise NotImplementedError()

    @abstractmethod
    def finish_return(self, loan: Loan) -> Loan:
        raise NotImplementedError()
