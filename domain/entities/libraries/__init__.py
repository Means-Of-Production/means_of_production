from __future__ import annotations
from typing import TYPE_CHECKING

# Import non-circular dependencies at runtime
from .library_fee import LibraryFee

# Use TYPE_CHECKING for potentially circular imports
if TYPE_CHECKING:
    from .library import Library
    from .base_library import BaseLibrary
    from .distributed_library import DistributedLibrary
    from .simple_library import SimpleLibrary


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "Library":
        from .library import Library

        return Library
    elif name == "BaseLibrary":
        from .base_library import BaseLibrary

        return BaseLibrary
    elif name == "DistributedLibrary":
        from .distributed_library import DistributedLibrary

        return DistributedLibrary
    elif name == "SimpleLibrary":
        from .simple_library import SimpleLibrary

        return SimpleLibrary
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Library",
    "LibraryFee",
    "BaseLibrary",
    "DistributedLibrary",
    "SimpleLibrary",
]
