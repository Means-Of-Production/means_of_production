from abc import abstractmethod
from typing import Self, Sequence, TYPE_CHECKING
from domain.entities.entity import Entity
from domain.value_items.borrower_verification_flags import BorrowerVerificationFlags

if TYPE_CHECKING:
    from domain.entities.libraries import Library, LibraryFee


class Borrower(Entity):
    """Abstract base class representing a library borrower."""

    library: "Library"
    verification_flags: list[BorrowerVerificationFlags]

    @property
    @abstractmethod
    def fees(self) -> Sequence["LibraryFee"]:
        """Get all fees associated with this borrower."""
        raise NotImplementedError

    @abstractmethod
    def apply_fee(self, fee: "LibraryFee") -> Self:
        """Apply a new fee to this borrower."""
        raise NotImplementedError
