from typing import Iterable, Self
from datetime import datetime, timezone

from pydantic import PrivateAttr

from domain.entities.lenders.lender import Lender
from domain.entities.loans import Loan
from domain.entities.people import Person
from domain.entities.thing import Thing
from domain.value_items import ID, Location, ThingStatus, LoanStatus
from domain.value_items.exceptions import ReturnNotStartedError


class IndividualDistributedLender(Person, Lender):
    _items: list[Thing] = PrivateAttr(default_factory=list)
    id: ID
    return_location_override : Location | None = None

    @property
    def items(self) -> Iterable[Thing]:
        return self._items

    def add_item(self, item: Thing) -> Self:
        self._items.append(item)
        return self

    def start_return(self, loan: Loan) -> Loan:
        if loan.item.status != ThingStatus.BORROWED:
            raise ReturnNotStartedError()
        loan.date_returned = datetime.now(tz=timezone.utc).date
        loan.status = LoanStatus.RETURN_STARTED
        return loan

    def finish_return(self, loan: Loan) -> Loan:
        if loan.status != LoanStatus.WAITING_ON_LENDER_ACCEPTANCE and loan.status != LoanStatus.RETURN_STARTED:
            raise ReturnNotStartedError()
        loan.status = LoanStatus.RETURNED
        return loan

    def get_preferred_return_location(self, item: Thing) -> Location:
        if self.return_location_override:
            return self.return_location_override
        return item.storage_location