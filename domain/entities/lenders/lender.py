from abc import abstractmethod
from typing import Iterable

from domain.entities.entity import Entity
from domain.entities.loan import Loan
from domain.entities.thing import Thing
from domain.value_items import Location


class Lender(Entity):
    @property
    @abstractmethod
    def items(self) -> Iterable[Thing]:
        raise NotImplementedError()

    @abstractmethod
    async def start_return(self, loan: Loan) -> Loan:
        raise NotImplementedError()

    @abstractmethod
    async def finish_return(self, loan: Loan) -> Loan:
        raise NotImplementedError()

    @property
    @abstractmethod
    def preferred_return_location(self) -> Location:
        raise NotImplementedError()
