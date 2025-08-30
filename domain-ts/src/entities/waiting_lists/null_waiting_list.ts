import { WaitingList, Reservation } from './waiting_list';
import { Borrower } from '../borrower';

export class NullWaitingList extends WaitingList {
  add(_: Borrower): this { return this; }
  find_next_borrower(): Borrower | null { return null; }
  is_on_list(_: Borrower): boolean { return false; }
  process_reservation_expired(_: Reservation): this { return this; }
  cancel(_: Borrower): this { return this; }
  get_reservation_time(): { days: number } { return { days: 0 }; }
}
