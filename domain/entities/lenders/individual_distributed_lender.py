from typing import Iterable

from pydantic import PrivateAttr

from domain.entities.lenders.lender import Lender
from domain.entities.loans import Loan
from domain.entities.people import Person
from domain.entities.thing import Thing
from domain.value_items import ID, Location, ThingStatus


class IndividualDistributedLender(Person, Lender):
    _items: list[Thing] = PrivateAttr(default_factory=list)
    id: ID
    return_location_override : Location | None = None

    @property
    def items(self) -> Iterable[Thing]:
        return self._items

    def start_return(self, loan: Loan) -> Loan:
        if(loan.item.status != ThingStatus.BORROWED):
            raise ReturnNotStartedError()
        loan.date_returned

    def finish_return(self, loan: Loan) -> Loan:
        pass