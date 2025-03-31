from typing import Iterable, Type, TypeVar
from .base_in_memory_repository import BaseInMemoryRepository
from domain.entities.libraries import Library
from domain.entities.libraries.simple_library import SimpleLibrary
from domain.entities.libraries.distributed_library import DistributedLibrary
from domain.entities.people import Person
from domain.value_items.location.physical_area import PhysicalArea

T = TypeVar("T", bound=Library)

class LibraryRepository(BaseInMemoryRepository[Library]):
    def __init__(self, libraries: Iterable[Library] = ()) -> None:
        """Initialize repository with optional libraries."""
        super().__init__(libraries)

    def get_id_from_entity(self, entity: Library) -> str:
        """Return unique identifier for a library entity."""
        return entity.entity_id or entity.name

    def get_libraries_person_can_use(self, person: Person) -> Iterable[Library]:
        """Retrieve libraries that a person can access."""
        return (
            library for library in self.get_all()
            if any(borrower.person.entity_id == person.entity_id for borrower in library.borrowers)
        )

    def create(self, entity: Library) -> Library:
        """Create a new library instance based on its type."""
        library_class: Type[Library]
        kwargs = {
            "entity_id": self.new_id(),
            "name": entity.name,
            "administrator": entity.administrator,
            "max_fines_before_suspension": entity.max_fines_before_suspension,
            "waiting_list_factory": entity.waiting_list_factory,
            "loans": entity.get_loans(),
            "money_factory": entity.money_factory,
            "mop_server": entity.mop_server,
            "fee_schedule": entity.fee_schedule,
        }

        if isinstance(entity, SimpleLibrary):
            library_class = SimpleLibrary
            kwargs["location"] = entity.location
        elif isinstance(entity, DistributedLibrary):
            library_class = DistributedLibrary
            kwargs["location"] = entity.location if isinstance(entity.location, PhysicalArea) else None
            kwargs["default_loan_time"] = entity.default_loan_time
        else:
            raise ValueError(f"Unknown library type: {type(entity).__name__}")

        return library_class(**kwargs)
