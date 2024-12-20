from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Sequence

from domain.entities.entity import Entity
from domain.entities.libraries import Library, LibraryFee
from domain.value_items import BorrowerVerificationFlags


class BaseBorrower(Entity):
    library: Library  # library this borrower is a member of
    verification_flags: list[BorrowerVerificationFlags]  # what flags the borrower has done

    @property
    @abstractmethod
    def fees(self) -> Sequence[LibraryFee]:
        pass

    @abstractmethod
    def apply_fee(self, fee: LibraryFee) -> BaseBorrower:
        raise NotImplementedError()