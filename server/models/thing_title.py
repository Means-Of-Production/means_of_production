from typing import Optional

from pydantic import BaseModel, Field


class ThingTitle(BaseModel):
    name: str = Field(..., description='The name of the thing')
    upc: Optional[str] = Field(
        None, description='Universal Product Code (if applicable)'
    )
    isbn: Optional[str] = Field(
        None, description='International Standard Book Number (if applicable)'
    )
    description: Optional[str] = Field(
        None, description='A brief description of the thing'
    )