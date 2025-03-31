from datetime import datetime, timedelta

class TimeInterval:
    """
    Represents a time interval in milliseconds.
    """

    def __init__(self, milliseconds: int):
        self.milliseconds = milliseconds

    def add_to_date(self, date: datetime) -> datetime:
        """
        Adds the interval to the given date.
        """
        return date + timedelta(milliseconds=self.milliseconds)

    def from_now(self) -> datetime:
        """
        Returns a datetime object representing the current time plus this interval.
        """
        return self.add_to_date(datetime.now())

    @staticmethod
    def from_days(days: int) -> "TimeInterval":
        """
        Creates a TimeInterval instance from a given number of days.
        """
        milliseconds = days * 24 * 60 * 60 * 1000
        return TimeInterval(milliseconds)
