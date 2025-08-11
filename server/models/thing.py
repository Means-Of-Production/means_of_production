from typing import List, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field

from .money import Money
from .physical_location import PhysicalLocation
from .status import Status
from .thing_title import ThingTitle


class Thing(BaseModel):
    thing_id: UUID = Field(..., description="A unique identifier for the thing")
    title: ThingTitle
    description: Optional[str] = Field(
        None, description="A detailed description of the thing"
    )
    owner_id: UUID = Field(..., description="The ID of the owner of the thing")
    storage_location: PhysicalLocation
    image_urls: Optional[List[AnyUrl]] = Field(
        None, description="URLs of images of the thing"
    )
    purchase_cost: Optional[Money] = None
    status: Status = Field(..., description="The status of a thing")
