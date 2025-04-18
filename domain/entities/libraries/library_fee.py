from domain.entities.entity import Entity
from domain.value_items import ID


class LibraryFee(Entity):
    library_fee_id: ID
    library_id: ID

    @property
    def entity_id(self) -> ID:
        return self.library_fee_id
