from __future__ import annotations

from urllib.parse import ParseResult, urlparse

from pydantic import BaseModel


class URL(BaseModel):
    value: ParseResult

    model_config = {"frozen": True}

    @classmethod
    def try_parse(cls, url_string: str) -> URL | None:
        if not url_string:
            return None
        res = urlparse(url_string)
        return URL(value=res)

    @classmethod
    def parse(cls, url_string: str) -> URL:
        res = urlparse(url_string)
        return URL(value=res)

    def __str__(self) -> str:
        return self.value.geturl()

    def __hash__(self) -> int:
        return hash(self.value)
