from enum import Enum


class BorrowerVerificationFlags(Enum):
    PHONE_NUMBER = ("PHONE_NUMBER",)
    EMAIL = ("EMAIL",)
    ID_SCANNED = ("ID_SCANNED",)
    DEPOSIT = "DEPOSIT"
