from datetime import date, timezone

from pydantic import PrivateAttr, field_validator, computed_field

from domain.entities.entity import Entity
from domain.entities.thing import Thing
from domain.entities.borrower import Borrower
from domain.entities.lenders import Lender

from domain.value_items import Location, DueDate, ID, LoanStatus

class Loan(Entity):
    loan_id: ID
    item: Thing
    due_date: DueDate
    borrower: Borrower
    location: Location
    _status: LoanStatus
    return_location: Location
    date_returned: date | None

    @classmethod
    @field_validator("_date_returned", mode="after")
    def validate_utc(cls, value):
        if value is not None:
            if value.tzinfo is None or value.tzinfo != timezone.utc:
                raise ValueError("The 'date' field must be in UTC timezone if populated.")

        return value

    @property
    def lender(self) -> Lender:
        return self.item.owner

    @property
    def id(self) -> ID:
        return self.loan_id

    @property
    def active(self) -> bool:
        return self._status == LoanStatus.BORROWED

    @property
    def status(self) -> LoanStatus:
        return self._status

    @status.setter
    def status(self, value: LoanStatus):
        valid_new_statuses = []
        match self._status:
            case LoanStatus.BORROWED:
                valid_new_statuses = [LoanStatus.RETURN_STARTED, LoanStatus.OVERDUE]
            case LoanStatus.OVERDUE:
                valid_new_statuses = [LoanStatus.RETURN_STARTED]
            case LoanStatus.RETURN_STARTED:
                valid_new_statuses = [
                    LoanStatus.WAITING_ON_LENDER_ACCEPTANCE,
                    LoanStatus.RETURNED,
                    LoanStatus.RETURNED_DAMAGED
                ]
            case LoanStatus.WAITING_ON_LENDER_ACCEPTANCE:
                valid_new_statuses = [
                    LoanStatus.RETURNED,
                    LoanStatus.RETURNED_DAMAGED,
                    LoanStatus.OVERDUE
                ]
            case LoanStatus.RETURNED_DAMAGED | LoanStatus.RETURNED:
                valid_new_statuses = []

        if value not in valid_new_statuses:
            raise ValueError(f"Cannot change loan status from '{self._status}' to '{value}'.")
        self._status = value

    @property
    def is_permanent_loan(self) -> bool:
        return self.due_date.date is None