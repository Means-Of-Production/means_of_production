from domain.entities import Borrower
from domain.value_items.exceptions import ResourceNotFoundException
from .base_in_memory_repository import BaseInMemoryRepository
from typing import Generator
from domain.entities import Person, IBorrower


class BorrowerRepository(BaseInMemoryRepository[IBorrower]):
    def __init__(self) -> None:
        super().__init__()

    def get_borrowers_for_person(self, person: Person) -> Generator[IBorrower, None, None]:
        for borrower in self.get_all():
            if borrower.person.entity_id == person.entity_id:
                yield borrower

    def create(self, entity: IBorrower) -> IBorrower:
        return Borrower(
            self.new_id(),
            entity.person,
            entity.library,
            list(entity.verification_flags),
            list(entity.fees)
        )
