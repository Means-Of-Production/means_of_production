from abc import ABC, abstractmethod

from domain.value_items import ID


class Entity(ABC):
    @property
    @abstractmethod
    def entity_id(self) -> ID:
        pass

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.entity_id == other.entity_id
