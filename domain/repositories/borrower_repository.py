from typing import Iterable
from domain.entities import Borrower, Person
from .base_in_memory_repository import BaseInMemoryRepository


class BorrowerRepository(BaseInMemoryRepository[Borrower]):
    def __init__(self) -> None:
        super().__init__()

    def get_borrowers_for_person(self, person: Person) -> Iterable[Borrower]:
        """Retrieve borrowers associated with a given person."""
        for borrower in self.get_all():
            if borrower.person.entity_id == person.entity_id:
                yield borrower

    def create(self, entity: Borrower) -> Borrower:
        """Create a new Borrower instance."""
        return Borrower(
            self.new_id(),
            entity.person,
            entity.library,
            list(entity.verification_flags),
            list(entity.fees),
        )
