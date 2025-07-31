from __future__ import annotations

from pydantic import BaseModel, Field

class Distance(BaseModel):
    model_config = {"frozen": True}
    kilometers: float = Field(ge=0.0)

    def __eq__(self, other) -> bool:
        return self.kilometers == other.kilometers

    def __lt__(self, other) -> bool:
        return self.kilometers < other.kilometers

    def __gt__(self, other) -> bool:
        return self.kilometers > other.kilometers

    def __le__(self, other) -> bool:
        return self.kilometers <= other.kilometers

    def __ge__(self, other) -> bool:
        return self.kilometers >= other.kilometers

    @classmethod
    def from_miles(cls, miles: float) -> Distance:
        return cls(kilometers=(miles / 1.60934))

    @property
    def miles(self) -> float:
        return self.kilometers * 1.60934

