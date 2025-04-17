from typing import Dict, Iterable, List

from domain.value_items import ID
from domain.value_items.thing_title import ThingTitle
from domain.entities import Thing
from domain.entities.libraries import Library
from domain.value_items.exceptions import EntityNotAssignedIdError


class LibrarySearchResult:
    def __init__(self, library: Library):
        self.library: Library = library
        self._things: List[Thing] = []

    def add_thing(self, item: Thing) -> "LibrarySearchResult":
        """Adds an item to the library's search result and returns the instance."""
        self._things.append(item)
        return self

    @property
    def things(self) -> Iterable[Thing]:
        """Returns an iterable of the things available in this library."""
        return iter(self._things)

    @property
    def num_copies(self) -> int:
        """Returns the number of copies available in the library."""
        return len(self._things)


class TitleSearchResult:
    def __init__(self, title: ThingTitle):
        self.title: ThingTitle = title
        self._library_results: Dict[ID, LibrarySearchResult] = {}

    @property
    def num_copies(self) -> int:
        """Returns the total number of copies available across all libraries."""
        return sum(lr.num_copies for lr in self._library_results.values())

    @property
    def library_results(self) -> Iterable[LibrarySearchResult]:
        """Returns an iterable of LibrarySearchResult instances."""
        return self._library_results.values()

    def get_for_library(self, library: Library) -> LibrarySearchResult:
        """Gets or creates a LibrarySearchResult for the given library."""
        if not getattr(library, "id", None):
            raise EntityNotAssignedIdError(
                f"Library {library.name} has not yet been saved!"
            )

        if library.library_id not in self._library_results:
            self._library_results[library.library_id] = LibrarySearchResult(library)

        return self._library_results[library.library_id]
