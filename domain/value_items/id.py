from uuid import UUID

from pydantic import BaseModel


class ID(BaseModel):
    id: UUID

    model_config = {"frozen": True}

    def __eq__(self, other):
        if not isinstance(other, ID):
            return False
        return self.id == other.id
