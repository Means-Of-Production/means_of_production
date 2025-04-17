from domain.value_items.url import URL
from domain.value_items.location.virtual_location import VirtualLocation


class MOPServer(VirtualLocation):
    def __init__(self, url: str, version: str):
        super().__init__(url=URL.parse(url))
        self.version = version

    @classmethod
    def localhost(cls) -> "MOPServer":
        return cls("https://localhost", "0.0.0")
