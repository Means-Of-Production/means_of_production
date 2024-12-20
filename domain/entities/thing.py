from typing import Final

from pydantic import Field

from domain.entities.entity import Entity
from domain.entities.lenders.lender import Lender
from domain.value_items import ID


class Thing(Entity):

    thing_id: Final[ID] = Field(..., const=True)  # pyright: ignore
    title: Final[str] = Field(..., const=True)  # pyright: ignore
    description: Final[str | None] = Field(default=None, const=True)  # pyright: ignore
    owner: Final[Lender] = Field(..., const=True)  # pyright: ignore

    @property
    def id(self) -> ID:
        return self.thing_id