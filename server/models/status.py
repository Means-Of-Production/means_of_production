from enum import Enum


class Status(Enum):
    READY = "READY"
    BORROWED = "BORROWED"
    DAMAGED = "DAMAGED"
    RESERVED = "RESERVED"
