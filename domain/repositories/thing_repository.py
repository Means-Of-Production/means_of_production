from domain.entities import Thing
from domain.repositories.base_in_memory_repository import BaseInMemoryRepository


class ThingRepository(BaseInMemoryRepository[Thing]):
    pass
