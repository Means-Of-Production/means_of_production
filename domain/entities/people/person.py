from dataclasses import dataclass

from pydantic import Field

from domain.entities.entity import Entity
from domain.value_items import PersonName, EmailAddress, ID


@dataclass(frozen=True)
class Person(Entity):
    """
    A domain entity representing a person in the system.
    Inherits from base Entity class to mark this as a domain entity.
    """

    person_id: ID
    name: PersonName
    emails: list[EmailAddress] = Field(default_factory=list)

    @property
    def entity_id(self) -> ID:
        return self.person_id

    def __post_init__(self):
        """Initialize with empty email list if none provided"""
        if self.emails is None:
            object.__setattr__(self, "emails", [])

    def __eq__(self, other: object) -> bool:
        """Entity equality comparison based on identity"""
        if not isinstance(other, Person):
            return False
        return self.person_id == other.person_id
