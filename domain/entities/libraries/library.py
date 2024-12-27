from abc import abstractmethod
from typing import Iterable

from domain.entities.entity import Entity
from domain.entities.borrower import Borrower
from domain.entities.thing import Thing
from domain.entities.people import Person
from domain.value_items import ID, DueDate, Location, ThingTitle
from domain.entities.loans import Loan


class Library(Entity):
    library_id: ID
    administrator: Person
    location: Location
    name: str

    @abstractmethod
    @property
    def all_things(self) -> Iterable[Thing]:
        raise NotImplementedError()

    @abstractmethod
    @property
    def available_things(self) -> Iterable[Thing]:
        raise NotImplementedError()

    @abstractmethod
    @property
    def all_titles(self) -> Iterable[ThingTitle]:
        raise NotImplementedError()

    @abstractmethod
    @property
    def available_titles(self) -> Iterable[ThingTitle]:
        raise NotImplementedError()

    @abstractmethod
    @property
    def borrowers(self) -> Iterable[Borrower]:
        raise NotImplementedError()

    def can_borrow(self, borrower: Borrower) -> bool:
        return borrower in self.borrowers

    @abstractmethod
    def borrow(self, thing: Thing, borrower: Borrower, until: DueDate) -> Loan:
        raise NotImplementedError()

    @abstractmethod
    def start_return(self, loan: Loan) -> Loan:
        raise NotImplementedError()

    @abstractmethod
    def finish_return(self, loan: Loan) -> Loan:
        raise NotImplementedError()

    @abstractmethod
    def reserve_item(self, title: ThingTitle, borrower: Borrower) -> WaitingList:
        raise NotImplementedError()
