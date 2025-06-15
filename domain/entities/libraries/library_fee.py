from domain.entities.entity import Entity
from domain.value_items import ID, FeeStatus, Money


class LibraryFee(Entity):
    library_fee_id: ID
    library_id: ID
    amount: Money
    status: FeeStatus
    charged_for_id: ID

    @property
    def entity_id(self) -> ID:
        return self.library_fee_id
