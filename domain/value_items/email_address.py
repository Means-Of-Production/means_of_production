from pydantic import BaseModel


class EmailAddress(BaseModel):
    model_config = {"frozen": True}
    value: str

    def __eq__(self, other):
        if not isinstance(other, EmailAddress):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)