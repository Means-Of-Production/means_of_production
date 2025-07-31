from __future__ import annotations

from math import radians, sin, cos, sqrt, atan2
from pydantic import Field

from domain.value_items.location.location import Location
from domain.value_items.location.distance import Distance


class PhysicalLocation(Location):
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    street_address: str = Field(...)
    city: str = Field(...)
    state: str = Field(...)
    zip_code: str = Field(...)
    country: str = Field(...)

    model_config = {"frozen": True}

    def __eq__(self, other) -> bool:
        if not isinstance(other, PhysicalLocation):
            return False
        if self.latitude and self.latitude != other.latitude:
            return False
        if self.longitude and self.longitude != other.longitude:
            return False
        return (
            self.street_address == other.street_address
            and self.city == other.city
            and self.state == other.state
            and self.zip_code == other.zip_code
        )

    def contains(self, other: Location) -> bool:
        return self == other

    def distance(self, other: PhysicalLocation) -> Distance:
        """
        Calculate the distance between two PhysicalLocation objects.
        Returns a Distance object if both locations have latitude and longitude set.
        Uses the Haversine formula to calculate the great-circle distance.

        Args:
            other: The other PhysicalLocation to calculate distance to

        Returns:
            Distance: The distance between the two locations in kilometers

        Raises:
            ValueError: If either location is missing latitude or longitude
        """
        if self.latitude is None or self.longitude is None:
            raise ValueError("This location does not have latitude and longitude set")
        if other.latitude is None or other.longitude is None:
            raise ValueError(
                "The other location does not have latitude and longitude set"
            )

        # Earth's radius in kilometers
        earth_radius = 6371.0

        # Convert latitude and longitude from degrees to radians
        lat1 = radians(self.latitude)
        lon1 = radians(self.longitude)
        lat2 = radians(other.latitude)
        lon2 = radians(other.longitude)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance_km = earth_radius * c

        return Distance(kilometers=distance_km)
