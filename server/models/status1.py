from enum import Enum


class Status1(Enum):
    READY = "READY"
    BORROWED = "BORROWED"
    DAMAGED = "DAMAGED"
    RESERVED = "RESERVED"
    ANY = "ANY"
