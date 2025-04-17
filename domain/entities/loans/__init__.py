from __future__ import annotations
from typing import TYPE_CHECKING

# Use TYPE_CHECKING for potentially circular imports
if TYPE_CHECKING:
    from domain.entities.loans.loan import Loan


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "Loan":
        from domain.entities.loans.loan import Loan

        return Loan
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["Loan"]
