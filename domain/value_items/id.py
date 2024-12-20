from uuid import UUID

from pydantic import BaseModel


class ID(BaseModel):
    id: UUID
