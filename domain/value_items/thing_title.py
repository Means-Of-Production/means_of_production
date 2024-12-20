from pydantic import BaseModel


class ThingTitle(BaseModel):
    name: str
    upc: str | None = None
    isbn: str | None = None
    description: str | None = None

    model_config = {"frozen": True}

    def __eq__(self, other):
        if not isinstance(other, ThingTitle):
            return False
        if self.name != other.name:
            return False
        if self.upc and other.upc and self.upc != other.upc:
            return False
        if self.isbn and other.isbn and self.isbn != other.isbn:
            return False
        return True

    def __hash__(self):
        return hash(self.name.replace("_", "-").lower())
