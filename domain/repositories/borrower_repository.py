from typing import Iterable

from domain.entities import Person, PersonBorrower

from .base_in_memory_repository import BaseInMemoryRepository


class BorrowerRepository(BaseInMemoryRepository[PersonBorrower]):
    def __init__(self) -> None:
        super().__init__()

    def get_borrowers_for_person(self, person: Person) -> Iterable[PersonBorrower]:
        """Retrieve borrowers associated with a given person."""
        for borrower in self.get_all():
            if borrower.entity_id == person.entity_id:
                yield borrower
