from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from domain.value_items import ID
from domain.value_items.user_roles import UserRoles


class User(BaseModel):
    user_id: ID
    email: List[EmailStr] = Field(default_factory=list)
    token: Optional[str] = None
    roles: List[UserRoles] = []
