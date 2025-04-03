from abc import ABC, abstractmethod
from domain.value_items.location import PhysicalArea, PhysicalLocation

class GeocoderService(ABC):
    @abstractmethod
    def get_current_location(self, search_string: str) -> PhysicalLocation:
        pass

    @abstractmethod
    def is_within(self, location: PhysicalLocation, area: PhysicalArea) -> bool:
        pass
