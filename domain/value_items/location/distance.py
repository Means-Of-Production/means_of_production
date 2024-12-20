from pydantic import BaseModel, Field

MILES_CONVERSION = 0.6214


class Distance(BaseModel):
    kilometers: float = Field(...)

    model_config = {"frozen": True}

    @property
    def miles(self) -> float:
        return self.kilometers * MILES_CONVERSION

    def __eq__(self, other):
        return self.kilometers == other.kilometers

    def __lt__(self, other):
        return self.kilometers < other.kilometers

    @classmethod
    def from_miles(cls, miles: float):
        return cls(kilometers=(miles / MILES_CONVERSION))
