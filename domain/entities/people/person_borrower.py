from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Self, Sequence
from pydantic import PrivateAttr
from domain.entities.people.person import Person
from domain.entities.people.borrower import Borrower


if TYPE_CHECKING:
    from domain.entities.libraries.library_fee import LibraryFee

class PersonBorrower(Person, Borrower):
    _fees = PrivateAttr(default_factory=list)

    @property
    def fees(self) -> Sequence[LibraryFee]:
        return self._fees

    def apply_fee(self, fee: LibraryFee) -> Self:
        self._fees.append(fee)
        return self
