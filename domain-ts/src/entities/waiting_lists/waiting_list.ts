import { Entity } from '../entity';
import { Borrower } from '../borrower';
import { Thing } from '../thing';
import { ID, ReservationStatus, ThingStatus } from '../../value_items';

export abstract class WaitingList extends Entity {
  waiting_list_id: ID;
  item: Thing;
  current_reservation: Reservation | null = null;
  expired_reservations: Reservation[] = [];

  constructor(params: { waiting_list_id?: ID; item: Thing }) {
    super();
    this.waiting_list_id = params.waiting_list_id ?? ID.generate();
    this.item = params.item;
  }

  get entity_id(): ID { return this.waiting_list_id; }

  abstract add(borrower: Borrower): this;
  abstract find_next_borrower(): Borrower | null;
  abstract is_on_list(borrower: Borrower): boolean;
  abstract process_reservation_expired(reservation: Reservation): this;
  abstract cancel(borrower: Borrower): this;
  abstract get_reservation_time(): { days: number };

  clear_current_reservation(): void { this.current_reservation = null; }

  reserve_item_for_next_borrower(): Reservation {
    if (this.current_reservation) {
      throw new Error('This item already has a reservation, please remove that first');
    }
    const next_borrower = this.find_next_borrower();
    if (!next_borrower) throw new Error('No borrower is waiting for this item!');

    const days = this.get_reservation_time().days;
    const good_until = new Date();
    good_until.setDate(good_until.getDate() + days);

    this.item.status = ThingStatus.RESERVED;

    const res = new Reservation({
      reservation_id: ID.generate(),
      holder: next_borrower,
      item: this.item,
      good_until,
      status: ReservationStatus.ASSIGNED,
    });

    this.cancel(next_borrower);
    this.current_reservation = res;
    return res;
  }
}

export class Reservation extends Entity {
  reservation_id: ID;
  holder: Borrower;
  item: Thing;
  good_until: Date;
  private _status: ReservationStatus;

  constructor(params: { reservation_id: ID; holder: Borrower; item: Thing; good_until: Date; status: ReservationStatus }) {
    super();
    this.reservation_id = params.reservation_id;
    this.holder = params.holder;
    this.item = params.item;
    this.good_until = params.good_until;
    this._status = params.status;
  }

  get entity_id(): ID { return this.reservation_id; }
  get status(): ReservationStatus { return this._status; }
  set status(status: ReservationStatus) {
    let valid: ReservationStatus[] = [];
    if (this.status === ReservationStatus.ASSIGNED) valid = [ReservationStatus.BORROWER_NOTIFIED];
    else if (this.status === ReservationStatus.BORROWER_NOTIFIED) valid = [ReservationStatus.EXPIRED, ReservationStatus.BORROWED];
    else if (this.status === ReservationStatus.BORROWED) valid = [];
    else if (this.status === ReservationStatus.EXPIRED) valid = [];
    else if (this.status === ReservationStatus.CANCELLED) valid = [];

    if (!valid.includes(status)) {
      throw new Error('InvalidReservationStateTransitionError');
    }
    this._status = status;
  }
}
