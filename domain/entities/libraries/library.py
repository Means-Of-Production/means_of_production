from abc import abstractmethod
from typing import Iterable, TYPE_CHECKING

from domain.entities.entity import Entity
from domain.entities.loans import Loan
from domain.entities.people import Borrower, Person
from domain.entities.waiting_lists import WaitingList

from domain.value_items import ID, DueDate, Location, ThingTitle

if TYPE_CHECKING:
    from domain.entities.thing import Thing


class Library(Entity):
    library_id: ID
    administrator: Person
    location: Location
    name: str

    @property
    @abstractmethod
    def all_things(self) -> Iterable[Thing]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def available_things(self) -> Iterable[Thing]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def all_titles(self) -> Iterable[ThingTitle]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def available_titles(self) -> Iterable[ThingTitle]:
        raise NotImplementedError()

    @property
    @abstractmethod
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
