from abc import ABC, abstractmethod
from uuid import uuid4
from typing import Generic, TypeVar, Iterable
from domain.value_items.exceptions import ConflictingKeyException, ResourceNotFoundException

T = TypeVar("T")
ID = TypeVar("ID")

class BaseInMemoryRepository(Generic[T], ABC):
    def __init__(self) -> None:
        self._entities: dict[ID, T] = {}

    def get_id_from_entity(self, entity: T) -> ID:
        entity_id = getattr(entity, "entity_id", None)
        if entity_id is None:
            raise ValueError(f"Entity {entity.__class__.__name__} does not have an id assigned!")
        return entity_id

    @abstractmethod
    def create(self, entity: T) -> T:
        """Assign an id to the entity if needed."""
        pass

    def new_id(self) -> str:
        return str(uuid4())

    def add(self, entity: T) -> T:
        if not hasattr(entity, "entity_id") or entity.entity_id is None:
            entity = self.create(entity)
        entity_id = self.get_id_from_entity(entity)
        if entity_id in self._entities:
            raise ConflictingKeyException(f"Entity with id {entity_id} already exists")
        self._entities[entity_id] = entity
        return entity

    def update(self, entity: T) -> T:
        entity_id = self.get_id_from_entity(entity)
        if entity_id not in self._entities:
            raise ResourceNotFoundException(f"Entity with id {entity_id} does not exist")
        self._entities[entity_id] = entity
        return entity

    def get(self, entity_id: ID) -> T | None:
        return self._entities.get(entity_id, None)

    def get_all(self) -> Iterable[T]:
        yield from self._entities.values()

    def delete(self, entity_id: ID) -> bool:
        if entity_id not in self._entities:
            raise ResourceNotFoundException(f"Entity with id {entity_id} not found")
        del self._entities[entity_id]
        return True
