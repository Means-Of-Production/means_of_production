from __future__ import annotations

from domain.value_items.location.location import Location
from domain.value_items.url import URL


class VirtualLocation(Location):
    url: URL

    model_config = {"frozen": True}

    def contains(self, other: VirtualLocation) -> bool:
        if not isinstance(other, VirtualLocation):
            return False
        return self.url == other.url
