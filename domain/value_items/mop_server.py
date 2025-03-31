from urllib.parse import urlparse
from .location import VirtualLocation

class MOPServer(VirtualLocation):
    def __init__(self, url: str, version: str):
        super().__init__(urlparse(url))
        self.version = version

    @classmethod
    def localhost(cls) -> "MOPServer":
        return cls("https://localhost", "0.0.0")
