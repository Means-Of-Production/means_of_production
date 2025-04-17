from __future__ import annotations
from typing import TYPE_CHECKING

# Use TYPE_CHECKING for potentially circular imports
if TYPE_CHECKING:
    from domain.entities.lenders.lender import Lender
    from domain.entities.lenders.individual_distributed_lender import (
        IndividualDistributedLender,
    )


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "Lender":
        from domain.entities.lenders.lender import Lender

        return Lender
    elif name == "IndividualDistributedLender":
        from domain.entities.lenders.individual_distributed_lender import (
            IndividualDistributedLender,
        )

        return IndividualDistributedLender
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["Lender", "IndividualDistributedLender"]
