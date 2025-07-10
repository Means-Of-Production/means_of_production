from datetime import datetime, timezone

from pydantic import PrivateAttr, field_validator

from domain.entities.entity import Entity
from domain.entities.thing import Thing
from domain.value_items import ID, DueDate, LoanStatus, Location


class Loan(Entity):
    model_config = {"frozen": False}

    loan_id: ID
    item: Thing
    due_date: DueDate
    borrower_id: ID
    location: Location | None = None
    _status: LoanStatus = PrivateAttr(default=LoanStatus.RETURNED)
    return_location: Location
    time_returned: datetime | None

    @classmethod
    @field_validator("time_returned", mode="after")
    def validate_utc(cls, value):
        if value is not None:
            if value.tzinfo is None or value.tzinfo != timezone.utc:
                raise ValueError(
                    "The 'date' field must be in UTC timezone if populated."
                )

        return value

    @property
    def lender_id(self) -> ID:
        return self.item.owner_id

    @property
    def entity_id(self) -> ID:
        return self.loan_id

    @property
    def active(self) -> bool:
        return self._status == LoanStatus.BORROWED

    @property
    def status(self) -> LoanStatus:
        if self.due_date and not self.due_date.is_after_now() and self._status == LoanStatus.BORROWED:
            self._status = LoanStatus.OVERDUE
        return self._status

    @status.setter
    def status(self, value: LoanStatus):
        valid_new_statuses = []
        match self._status:
            case LoanStatus.RETURNED:
                valid_new_statuses = [LoanStatus.BORROWED]
            case LoanStatus.BORROWED:
                valid_new_statuses = [LoanStatus.RETURN_STARTED, LoanStatus.OVERDUE]
            case LoanStatus.OVERDUE:
                valid_new_statuses = [LoanStatus.RETURN_STARTED]
            case LoanStatus.RETURN_STARTED:
                valid_new_statuses = [
                    LoanStatus.WAITING_ON_LENDER_ACCEPTANCE,
                    LoanStatus.RETURNED,
                    LoanStatus.RETURNED_DAMAGED,
                ]
            case LoanStatus.WAITING_ON_LENDER_ACCEPTANCE:
                valid_new_statuses = [
                    LoanStatus.RETURNED,
                    LoanStatus.RETURNED_DAMAGED,
                    LoanStatus.OVERDUE,
                ]
            case LoanStatus.RETURNED_DAMAGED | LoanStatus.RETURNED:
                valid_new_statuses = []

        if value not in valid_new_statuses:
            raise ValueError(
                f"Cannot change loan status from '{self._status}' to '{value}'."
            )
        self._status = value

    @property
    def is_permanent_loan(self) -> bool:
        return self.due_date.date is None
