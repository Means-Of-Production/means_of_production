from enum import Enum

class FeeStatus(Enum):
    OUTSTANDING = "OUTSTANDING"
    PAID = "PAID"
    IN_PAYMENT = "IN_PAYMENT"
    FORGIVEN = "FORGIVEN"
