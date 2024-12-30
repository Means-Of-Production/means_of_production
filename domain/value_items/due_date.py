from datetime import date, timezone

from pydantic import BaseModel, field_validator


class DueDate(BaseModel):
    date: date | None

    @classmethod
    @field_validator("date", mode="after")
    def validate_utc(cls, value):
        if value is not None:
            if value.tzinfo is None or value.tzinfo != timezone.utc:
                raise ValueError(
                    "The 'date' field must be in UTC timezone if populated."
                )
        return value

    def __lt__(self, other):
        if not self.date:
            return False
        return self.date < other.date

    def __gt__(self, other):
        if not self.date:
            return True
        return self.date > other.date

    def __eq__(self, other):
        if not isinstance(other, DueDate):
            return False
        if not self.date and not other.date:
            return True
        return self.date == other.date
