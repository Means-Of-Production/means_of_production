from __future__ import annotations
from datetime import datetime, timedelta

from pydantic import BaseModel


class TimeInterval(BaseModel):
    model_config = {"frozen": True}
    milliseconds: int
    
    def add_to_date(self, date: datetime) -> datetime:
        return date + timedelta(milliseconds=self.milliseconds)
    
    def from_now(self) -> datetime:
        return self.add_to_date(datetime.now())
    
    @classmethod
    def from_days(cls, days: int) -> TimeInterval:
        milliseconds = days * 24 * 60 * 60 * 1000
        return cls(milliseconds=milliseconds)
    
    def __eq__(self, other):
        if not isinstance(other, TimeInterval):
            return False
        return self.milliseconds == other.milliseconds
    
    def __hash__(self):
        return hash(self.milliseconds)