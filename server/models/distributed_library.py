from typing import Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field

from domain import Currency

from .area import Area
from .money import Money
from .person import Person
from .waiting_list_type import WaitingListType


class DistributedLibrary(BaseModel):
    library_id: Optional[UUID] = Field(
        None, description="A unique identifier for the library"
    )
    name: str
    administrator: Person
    area: Area = Field(
        ..., description="The physical area covered by this distributed library"
    )
    waiting_list_type: WaitingListType
    max_fines_before_suspension: Money
    currency: Currency
    default_loan_time: str = Field(
        ...,
        description="Duration of the default loan period (ISO 8601 duration format, e.g., 'P14D' for 14 days)",
    )
    mop_server_address: AnyUrl = Field(..., description="URL address of the MOP server")
    public_url: Optional[AnyUrl] = None
