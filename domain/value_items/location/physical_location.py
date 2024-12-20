from pydantic import Field

from domain.value_items.location.location import Location


class PhysicalLocation(Location):
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    street_address: str = Field(...)
    city: str = Field(...)
    state: str = Field(...)
    zip_code: str = Field(...)

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
