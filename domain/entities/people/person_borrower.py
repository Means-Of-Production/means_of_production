from typing import Sequence, Self

from pydantic import PrivateAttr

from domain.entities.libraries import LibraryFee
from domain.entities.people import Person
from domain.entities.people.borrower import Borrower


class PersonBorrower(Person, Borrower):
    _fees = PrivateAttr(default_factory=list)

    @property
    def fees(self) -> Sequence[LibraryFee]:
        return self._fees

    def apply_fee(self, fee: LibraryFee) -> Self:
        self._fees.append(fee)
        return self
