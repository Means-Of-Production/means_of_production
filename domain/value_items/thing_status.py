from enum import Enum


class ThingStatus(Enum):
    READY = ("READY",)
    BORROWED = ("BORROWED",)
    DAMAGED = ("DAMAGED",)
    RESERVED = "RESERVED"
