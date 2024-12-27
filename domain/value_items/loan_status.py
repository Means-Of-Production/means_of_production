from enum import Enum


class LoanStatus(Enum):
    BORROWED = "BORROWED"
    OVERDUE = "OVERDUE"
    RETURN_STARTED = "RETURN_STARTED"
    WAITING_ON_LENDER_ACCEPTANCE = "WAITING_ON_LEADER_ACCEPTANCE"
    RETURNED_DAMAGED = "RETURNED_DAMAGED"
    RETURNED = "RETURNED"