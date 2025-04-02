from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Dict, TYPE_CHECKING
from domain.entities import Thing
from domain.entities.people import Person
from domain.value_items import ThingTitle
from domain.value_items.title_search_request import TitleSearchRequest
from domain.value_items.title_search_result import TitleSearchResult

if TYPE_CHECKING:
    from domain.repositories.library_repository import LibraryRepository

class ITitleSearchService(ABC):
    """Interface for Title Search Service."""

    @abstractmethod
    def find(self, person: Person, search_request: TitleSearchRequest) -> Iterable[TitleSearchResult]:
        """Find titles based on search criteria for a given person."""
        pass


class TitleSearchService(ITitleSearchService):
    """Implementation of the Title Search Service."""
    
    def __init__(self, library_repository: LibraryRepository):
        # Local import to break circular dependency
        from domain.repositories.library_repository import LibraryRepository
        if not isinstance(library_repository, LibraryRepository):
            raise TypeError("library_repository must be a LibraryRepository instance")
        self.library_repository = library_repository

    def _matches(self, search_request: TitleSearchRequest, thing: Thing) -> bool:
        """Check if a thing matches the search request."""
        if not search_request.search_text:
            return True
        
        title: ThingTitle = thing.title
        return (
            search_request.search_text in title.name or
            search_request.search_text == title.isbn or
            search_request.search_text == title.upc
        )

    def find(self, person: Person, search_request: TitleSearchRequest) -> Iterable[TitleSearchResult]:
        """Find matching titles for the person based on search criteria."""
        libraries = self.library_repository.get_libraries_person_can_use(person)

        results_by_title_hash: Dict[str, TitleSearchResult] = {}

        for library in libraries:
            for thing in library.get_available_things():
                if self._matches(search_request, thing):
                    title_hash = thing.title.hash
                    if title_hash not in results_by_title_hash:
                        results_by_title_hash[title_hash] = TitleSearchResult(thing.title)

                    title_result = results_by_title_hash[title_hash]
                    lib_request = title_result.get_for_library(library)
                    lib_request.add_thing(thing)

        return results_by_title_hash.values()