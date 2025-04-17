from typing import Iterable, TypeVar
from .base_in_memory_repository import BaseInMemoryRepository
from domain.entities.libraries import Library
from domain.entities.people import Person
from ..value_items import ID

T = TypeVar("T", bound=Library)


class LibraryRepository(BaseInMemoryRepository[Library]):
    def create(self, entity: T) -> T:
        return entity

    def __init__(self, libraries: Iterable[Library] | None = None) -> None:
        if not libraries:
            libraries = []
        super().__init__(libraries)

    def get_id_from_entity(self, entity: Library) -> ID:
        return entity.entity_id

    def get_libraries_person_can_use(self, person: Person) -> Iterable[Library]:
        return (
            library
            for library in self.get_all()
            if any(
                borrower.person.entity_id == person.entity_id
                for borrower in library.borrowers
            )
        )
