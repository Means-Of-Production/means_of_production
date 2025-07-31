from domain.value_items.location.distance import Distance
from domain.value_items.location.location import Location
from domain.value_items.location.physical_location import PhysicalLocation


class PhysicalArea(Location):
    center_point: PhysicalLocation
    radius: Distance

    model_config = {"frozen": True}

    def contains(self, other: Location) -> bool:
        if isinstance(other, PhysicalLocation):
            # if the distance between our center is less than our radius, it is
            distance = self.center_point.distance(other)
            return distance < self.radius
        elif isinstance(other, PhysicalArea):
            # check if the other area is contained within us
            offset = self.center_point.distance(other.center_point)
            return offset + other.radius < self.radius
        raise ValueError(f"Cannot compute contain for location type {type(other)}")
