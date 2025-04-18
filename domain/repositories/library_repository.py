from typing import Iterable
from .base_in_memory_repository import BaseInMemoryRepository
from domain.entities import Library, SimpleLibrary, DistributedLibrary, Person
from domain.value_items.location.physical_area import PhysicalArea


class LibraryRepository(BaseInMemoryRepository[Library]):
    def __init__(self, libraries: Iterable[Library] = ()) -> None:
        super().__init__()
        for lib in libraries:
            self.add(lib)

    def get_libraries_person_can_use(self, person: Person) -> Iterable[Library]:
        """Retrieve libraries a person can access."""
        return (
            library for library in self.get_all()
            if any(borrower.person.entity_id == person.entity_id for borrower in library.borrowers)
        )

    def create(self, entity: Library) -> Library:
        if isinstance(entity, SimpleLibrary):
            return SimpleLibrary(
                self.new_id(),
                entity.name,
                entity.administrator,
                entity.location,
                entity.waiting_list_factory,
                entity.max_fines_before_suspension,
                entity.get_loans(),
                entity.money_factory,
                entity.mop_server,
                entity.fee_schedule,
            )

        if isinstance(entity, DistributedLibrary):
            return DistributedLibrary(
                self.new_id(),
                entity.name,
                entity.administrator,
                entity.max_fines_before_suspension,
                entity.waiting_list_factory,
                entity.get_loans(),
                entity.money_factory,
                entity.location if isinstance(entity.location, PhysicalArea) else None,
                entity.mop_server,
                entity.fee_schedule,
                entity.default_loan_time,
            )

        raise ValueError(f"Don't know how to handle library of type {type(entity).__name__} yet!")
