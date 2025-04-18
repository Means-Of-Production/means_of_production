from domain.entities import Person
from domain.repositories.base_in_memory_repository import BaseInMemoryRepository


class PersonRepository(BaseInMemoryRepository[Person]):
    def __init__(self):
        super().__init__()

    def get_id_field_name(self) -> str:
        return "person_id"
