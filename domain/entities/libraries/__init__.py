from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entities.libraries.library import Library
    from domain.entities.libraries.library_fee import LibraryFee

# Optional: Explicitly declare what should be available when importing the package
__all__ = ['Library', 'LibraryFee', 'BaseLibrary', 'DistributedLibrary']  # etc.