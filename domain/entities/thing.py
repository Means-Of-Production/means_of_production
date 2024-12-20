from pydantic import Field, PrivateAttr, computed_field

from domain.entities.entity import Entity
from domain.entities.lenders.lender import Lender
from domain.value_items import ID, Location, Money, ThingStatus, ThingTitle
from domain.value_items.exceptions import InvalidThingStateTransitionError


class Thing(Entity):
    thing_id: ID
    title: ThingTitle
    description: str | None
    owner: Lender
    storage_location: Location
    image_urls: list[str] = Field(default_factory=list)
    purchase_cost: Money | None

    _status: ThingStatus = PrivateAttr()

    @property
    def id(self) -> ID:
        return self.thing_id

    @computed_field
    @property
    def status(self) -> ThingStatus:
        return self._status

    @status.setter
    def status(self, value: ThingStatus):
        valid_next_statuses: list[ThingStatus] = []

        if self._status == ThingStatus.READY:
            valid_next_statuses = [ThingStatus.BORROWED, ThingStatus.RESERVED]
        elif self._status == ThingStatus.BORROWED:
            valid_next_statuses = [
                ThingStatus.READY,
                ThingStatus.RESERVED,
                ThingStatus.DAMAGED,
            ]
        elif self._status == ThingStatus.RESERVED:
            valid_next_statuses = [ThingStatus.READY, ThingStatus.BORROWED]
        elif self._status == ThingStatus.DAMAGED:
            # todo switch to repair path later
            valid_next_statuses = []

        if value not in valid_next_statuses:
            raise InvalidThingStateTransitionError(self._status, value)

        self._status = value
