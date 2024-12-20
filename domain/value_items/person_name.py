from pydantic import BaseModel


class PersonName(BaseModel):
    salutation: str | None = None
    first_name: str
    middle_name: str | None = None
    last_name: str
    suffix: str | None = None
