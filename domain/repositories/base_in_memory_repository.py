from typing import Generic, Iterable, TypeVar

from domain.entities import Entity
from domain.value_items import ID

T = TypeVar("T", bound=Entity)


class BaseInMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._entities: dict[ID, T] = {}

    def add(self, entity: T) -> T:
        if entity.entity_id in self._entities:
            raise ValueError(f"Entity with id {entity.entity_id} already exists")
        self._entities[entity.entity_id] = entity
        return entity

    def update(self, entity: T) -> T:
        if entity.entity_id not in self._entities:
            raise ValueError(f"Entity with id {entity.entity_id} does not exist")
        self._entities[entity.entity_id] = entity
        return entity

    def get(self, entity_id: ID) -> T | None:
        return self._entities.get(entity_id, None)

    def get_all(self) -> Iterable[T]:
        yield from self._entities.values()

    def __delete__(self, entity_id: ID) -> None:
        del self._entities[entity_id]
