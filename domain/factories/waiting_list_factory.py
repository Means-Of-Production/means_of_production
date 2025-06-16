
from domain.entities import Library, WaitingList, Thing
from domain.entities.waiting_lists import FirstComeFirstServeWaitingList, NullWaitingList
from domain.value_items import WaitingListType

class WaitingListFactory:
    @staticmethod
    def create_new_list(library: Library, item: Thing) -> WaitingList:
        match library.waiting_list_type:
            case WaitingListType.NONE:
                return NullWaitingList(item=item)
            case WaitingListType.FIRST_COME_FIRST_SERVE:
                return FirstComeFirstServeWaitingList(item=item)
        raise ValueError(f"Can't handle library type {library.waiting_list_type}")
