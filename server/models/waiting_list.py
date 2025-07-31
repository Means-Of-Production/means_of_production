from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .reservation import Reservation
from .thing import Thing


class WaitingList(BaseModel):
    waiting_list_id: UUID = Field(
        ..., description="A unique identifier for the waiting list"
    )
    item: Thing
    current_reservation: Optional[Reservation] = None
    expired_reservations: Optional[List[Reservation]] = None
