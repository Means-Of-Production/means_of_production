from abc import ABC, abstractmethod

from domain.value_items import ID


class Entity(ABC):
    @property
    @abstractmethod
    def id(self) -> ID:
        pass
