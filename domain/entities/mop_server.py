from domain.entities.entity import Entity
from domain.value_items import ID, URL


class MOPServer(Entity):
    id: ID
    base_url: URL

    @property
    def entity_id(self) -> ID:
        return self.id
