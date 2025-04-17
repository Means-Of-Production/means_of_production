from __future__ import annotations

from pydantic import BaseModel


class ID(BaseModel):
    value: str

    def __str__(self):
        return self.value

    @classmethod
    def parse(cls, id_string: str) -> ID:
        return ID(value=id_string)
