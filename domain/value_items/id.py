from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel


class ID(BaseModel):
    model_config = {"frozen": True}
    id: UUID

    def __eq__(self, other):
        if not isinstance(other, ID):
            return False
        return self.id == other.id

    @classmethod
    def parse(cls, value: str) -> ID:
        return ID(id=UUID(value))

    @classmethod
    def generate(cls) -> ID:
        return ID(id=uuid4())
