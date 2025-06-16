from domain.entities.thing import Thing
from domain.entities.waiting_lists.first_come_first_serve_waiting_list import (
    FirstComeFirstServeWaitingList,
)
from domain.entities.waiting_lists.null_waiting_list import NullWaitingList
from domain.entities.waiting_lists.waiting_list import WaitingList
from domain.value_items import WaitingListType


class WaitingListFactory:
    @staticmethod
    def create_new_list(library, item: Thing) -> WaitingList:
        match library.waiting_list_type:
            case WaitingListType.NONE:
                return NullWaitingList(item=item)
            case WaitingListType.FIRST_COME_FIRST_SERVE:
                return FirstComeFirstServeWaitingList(item=item)
        raise ValueError(f"Can't handle library type {library.waiting_list_type}")
