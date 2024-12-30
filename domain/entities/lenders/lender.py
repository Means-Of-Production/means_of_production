from abc import abstractmethod
from typing import Iterable

from domain.entities.entity import Entity
from domain.entities.loans import Loan
from domain.entities.thing import Thing


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
