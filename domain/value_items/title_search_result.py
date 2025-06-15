from typing import TYPE_CHECKING, Dict, Iterable, List

from pydantic import BaseModel

from domain import ID
from domain.value_items.thing_title import ThingTitle

if TYPE_CHECKING:
    from domain.entities.libraries.library import Library
    from domain.entities.thing import Thing


class LibrarySearchResult(BaseModel):
    model_config = {"frozen": False}  # Need to be mutable to add things
    library: "Library"
    _things: List["Thing"] = []

    def add_thing(self, item: "Thing") -> "LibrarySearchResult":
        self._things.append(item)
        return self

    @property
    def things(self) -> Iterable["Thing"]:
        return self._things

    @property
    def num_copies(self) -> int:
        return len(self._things)


class TitleSearchResult(BaseModel):
    model_config = {"frozen": False}  # Need to be mutable to add library results
    title: ThingTitle
    _library_results: Dict[ID, LibrarySearchResult] = {}

    @property
    def num_copies(self) -> int:
        return sum(lr.num_copies for lr in self._library_results.values())

    @property
    def library_results(self) -> Iterable[LibrarySearchResult]:
        return self._library_results.values()

    def get_for_library(self, library: "Library") -> LibrarySearchResult:
        if not library.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError

            raise EntityNotAssignedIdError(
                f"Library {library.name} has not yet been saved!"
            )

        result = self._library_results.get(library.entity_id)
        if not result:
            result = LibrarySearchResult(library=library)
            self._library_results[library.entity_id] = result
        return result
