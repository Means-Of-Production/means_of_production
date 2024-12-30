from abc import abstractmethod
from typing import Self, Sequence

from domain.entities.entity import Entity
from domain.entities.libraries import Library, LibraryFee
from domain.value_items import BorrowerVerificationFlags


class Borrower(Entity):
    library: Library  # the library this borrower is a member of
    verification_flags: list[BorrowerVerificationFlags]

    @property
    @abstractmethod
    def fees(self) -> Sequence[LibraryFee]:
        raise NotImplementedError

    @abstractmethod
    def apply_fee(self, fee: LibraryFee) -> Self:
        raise NotImplementedError
