from typing import Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field

from domain import Currency
from .money import Money
from .person import Person
from .physical_location import PhysicalLocation
from .waiting_list_type import WaitingListType


class SimpleLibrary(BaseModel):
    library_id: Optional[UUID] = Field(
        None, description="A unique identifier for the library"
    )
    name: str
    administrator: Person
    location: PhysicalLocation
    waiting_list_type: WaitingListType
    max_fines_before_suspension: Money
    currency: Currency
    default_loan_time: str = Field(
        ...,
        description="Duration of the default loan period (ISO 8601 duration format, e.g., 'P14D' for 14 days)",
    )
    mop_server_address: AnyUrl = Field(..., description="URL address of the MOP server")
    public_url: Optional[AnyUrl] = None
