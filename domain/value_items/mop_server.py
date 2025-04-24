from __future__ import annotations
from typing import ClassVar

from domain.value_items.location.virtual_location import VirtualLocation
from domain.value_items.url import URL


class MOPServer(VirtualLocation):
    version: str
    
    model_config = {"frozen": True}
    
    @classmethod
    def localhost(cls) -> MOPServer:
        return cls(url=URL.parse("https://localhost"), version="0.0.0")