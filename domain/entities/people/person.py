from pydantic import BaseModel, EmailStr, Field

from domain.entities.entity import Entity  # Remove if Entity isn't needed
from domain.value_items import ID, PersonName


class Person(BaseModel):  # Changed from Entity to BaseModel
    person_id: ID
    name: PersonName
    email: list[EmailStr] = Field(default_factory=list)

    @property
    def id(self) -> ID:
        return self.person_id