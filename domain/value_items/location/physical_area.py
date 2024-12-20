from typing import Final
from pydantic import BaseModel, Field

from domain.value_items.location.location import Location
from domain.value_items.location.physical_location import PhysicalLocation
from domain.value_items.location.distance import Distance


class PhysicalArea(Location):
    center_point: PhysicalLocation
    radius: Distance

    model_config = {"frozen": True}

    def contains(self, other: Location) -> bool:
        pass
