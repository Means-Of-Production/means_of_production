from datetime import date, datetime, timezone

from pydantic import BaseModel, field_validator


class DueDate(BaseModel):
    model_config = {"frozen": True}
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

        other_date: date
        if isinstance(other, DueDate):
            if not other.date:
                return True
            other_date = other.date
        elif isinstance(other, datetime):
            other_date = other.date()
        else:
            other_date = other
        return self.date < other_date

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
