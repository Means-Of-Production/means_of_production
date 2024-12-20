
from domain.value_items.location.distance import Distance
from domain.value_items.location.location import Location
from domain.value_items.location.physical_location import PhysicalLocation


class PhysicalArea(Location):
    center_point: PhysicalLocation
    radius: Distance

    model_config = {"frozen": True}

    def contains(self, other: Location) -> bool:
        pass
