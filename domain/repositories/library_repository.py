from typing import Iterable
from .base_in_memory_repository import BaseInMemoryRepository
from domain.entities import Library, Person


class LibraryRepository(BaseInMemoryRepository[Library]):
    def __init__(self, libraries: Iterable[Library] = ()) -> None:
        super().__init__()
        for lib in libraries:
            self.add(lib)

    def get_id_field_name(self) -> str:
        return "library_id"

    def get_libraries_person_can_use(self, person: Person) -> Iterable[Library]:
        """Retrieve libraries a person can access."""
        return (
            library for library in self.get_all()
            if any(borrower.entity_id == person.entity_id for borrower in library.borrowers)
        )
