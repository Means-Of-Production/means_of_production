import { WaitingList, Reservation } from './waiting_list';
import { Borrower } from '../borrower';

export class FirstComeFirstServeWaitingList extends WaitingList {
  members: Borrower[] = [];
  reservation_days: number = 3;
  private _expired_reservations: Reservation[] = [];

  add(borrower: Borrower): this {
    this.members.push(borrower);
    return this;
  }

  is_on_list(borrower: Borrower): boolean {
    const member_ids = this.members.map(b => b.entity_id.toString());
    return member_ids.includes(borrower.entity_id.toString());
  }

  find_next_borrower(): Borrower | null {
    if (this.members.length === 0) return null;
    return this.members[0];
  }

  get_reservation_time(): { days: number } {
    return { days: this.reservation_days };
  }

  process_reservation_expired(reservation: Reservation): this {
    reservation.status = reservation.status; // no state change specific here
    this._expired_reservations.push(reservation);
    this.clear_current_reservation();
    return this;
  }

  cancel(borrower: Borrower): this {
    this.members = this.members.filter(b => !b.entity_id.equals(borrower.entity_id));
    return this;
  }
}
