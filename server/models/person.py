from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Person(BaseModel):
    person_id: UUID = Field(..., description="A unique identifier for the person")
    salutation: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    emails: Optional[List[EmailStr]] = None
