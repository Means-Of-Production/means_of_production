import { Thing } from '../entities/thing';
import { WaitingList } from '../entities/waiting_lists/waiting_list';
import { FirstComeFirstServeWaitingList } from '../entities/waiting_lists/first_come_first_serve_waiting_list';
import { NullWaitingList } from '../entities/waiting_lists/null_waiting_list';
import { WaitingListType } from '../value_items/waiting_list_types';

export class WaitingListFactory {
  static create_new_list(library: { waiting_list_type: WaitingListType }, item: Thing): WaitingList {
    switch (library.waiting_list_type) {
      case WaitingListType.NONE:
        return new NullWaitingList({ item });
      case WaitingListType.FIRST_COME_FIRST_SERVE:
        return new FirstComeFirstServeWaitingList({ item });
      default:
        throw new Error(`Can't handle library type ${library.waiting_list_type}`);
    }
  }
}
