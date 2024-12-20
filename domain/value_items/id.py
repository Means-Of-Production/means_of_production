from uuid import UUID

from pydantic import BaseModel


class ID(BaseModel):
    id: UUID

    model_config = {"frozen": True}
