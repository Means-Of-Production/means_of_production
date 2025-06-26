from enum import Enum, auto


class WaitingListType(Enum):
    NONE = auto()
    QUADRATIC_WAITING_LIST = auto()
    FIRST_COME_FIRST_SERVE = auto()
