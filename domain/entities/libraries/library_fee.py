from pydantic import PrivateAttr

from domain.entities.entity import Entity
from domain.value_items import ID, FeeStatus, Money


class LibraryFee(Entity):
    model_config = {"frozen": False}

    library_fee_id: ID
    library_id: ID
    amount: Money
    _status: FeeStatus = PrivateAttr(default=FeeStatus.OUTSTANDING)
    charged_for_id: ID

    @property
    def status(self) -> FeeStatus:
        return self._status

    @status.setter
    def status(self, value: FeeStatus) -> None:
        self._status = value

    @property
    def entity_id(self) -> ID:
        return self.library_fee_id
