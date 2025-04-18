from pydantic import EmailStr, Field

from domain.entities.entity import Entity
from domain.value_items import ID, PersonName


class Person(Entity):
    person_id: ID
    name: PersonName
    email: list[EmailStr] = Field(default_factory=list)

    @property
    def entity_id(self) -> ID:
        return self.person_id
