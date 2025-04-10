from domain.entities.people import Person
from domain.repositories.base_in_memory_repository import BaseInMemoryRepository

class PersonRepository(BaseInMemoryRepository[Person]):
    def __init__(self):
        super().__init__()

    def create(self, entity: Person) -> Person:
        return Person(
            person_id=self.new_id(),
            name=entity.name,
            email=entity.email
        )
