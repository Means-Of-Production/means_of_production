from dataclasses import dataclass
from typing import List
from domain.entities.entity import Entity  
from domain.value_items import PersonName, EmailAddress

@dataclass(frozen=True)
class Person(Entity):
    """
    A domain entity representing a person in the system.
    Inherits from base Entity class to mark this as a domain entity.
    """
    name: PersonName
    emails: List[EmailAddress] = None

    def __post_init__(self):
        """Initialize with empty email list if none provided"""
        if self.emails is None:
            object.__setattr__(self, 'emails', [])

    def __eq__(self, other: object) -> bool:
        """Entity equality comparison based on identity"""
        if not isinstance(other, Person):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make entity hashable based on its identity"""
        return hash(self.id)