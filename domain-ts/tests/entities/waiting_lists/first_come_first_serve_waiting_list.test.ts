import { describe, it, expect } from 'vitest';
import { FirstComeFirstServeWaitingList } from '../../../src/entities/waiting_lists/first_come_first_serve_waiting_list';
import { WaitingList } from '../../../src/entities/waiting_lists/waiting_list';
import { WaitingListFactory } from '../../../src/factories/waiting_list_factory';
import { WaitingListType } from '../../../src/value_items/waiting_list_types';
import { Thing } from '../../../src/entities/thing';
import { ID } from '../../../src/value_items/id';
import { ThingTitle } from '../../../src/value_items/thing_title';
import { PhysicalLocation } from '../../../src/value_items/location/physical_location';
import { Person } from '../../../src/entities/people/person';
import { PersonBorrower } from '../../../src/entities/people/person_borrower';
import { PersonName } from '../../../src/value_items/person_name';
import { ThingStatus } from '../../../src/value_items/thing_status';
import { ReservationStatus } from '../../../src/value_items/reservation_status';

function makeThing(): Thing {
  return new Thing({
    thing_id: ID.generate(),
    title: new ThingTitle({ name: 'Saw' }),
    description: null,
    owner_id: ID.generate(),
    storage_location: new PhysicalLocation({ street_address: '1 Main', city: 'X', state: 'Y', zip_code: '00000', country: 'US' }),
  });
}

function makeBorrower(library_id: ID): PersonBorrower {
  return new PersonBorrower({
    person_id: ID.generate(),
    name: new PersonName({ first_name: 'B', last_name: 'R' }),
    library_id,
  });
}

describe('FirstComeFirstServeWaitingList', () => {
  it('add and is_on_list works', () => {
    const item = makeThing();
    const wl = new FirstComeFirstServeWaitingList({ item });
    const borrower = makeBorrower(ID.generate());
    expect(wl.is_on_list(borrower)).toBe(false);
    wl.add(borrower);
    expect(wl.is_on_list(borrower)).toBe(true);
  });

  it('find_next_borrower returns the first added', () => {
    const item = makeThing();
    const wl = new FirstComeFirstServeWaitingList({ item });
    const b1 = makeBorrower(ID.generate());
    const b2 = makeBorrower(ID.generate());
    wl.add(b1).add(b2);
    const nextB = wl.find_next_borrower();
    expect(nextB?.entity_id.equals(b1.entity_id)).toBe(true);
  });

  it('reserve_item_for_next_borrower sets reservation and item status RESERVED', () => {
    const item = makeThing();
    const wl = new FirstComeFirstServeWaitingList({ item });
    const b1 = makeBorrower(ID.generate());
    const b2 = makeBorrower(ID.generate());
    wl.add(b1).add(b2);
    const res = wl.reserve_item_for_next_borrower();
    expect(res.holder.entity_id.equals(b1.entity_id)).toBe(true);
    expect(item.status).toBe(ThingStatus.RESERVED);
    // b1 should be removed from list
    expect(wl.is_on_list(b1)).toBe(false);
  });

  it('cancel removes a borrower from the list', () => {
    const wl = new FirstComeFirstServeWaitingList({ item: makeThing() });
    const b1 = makeBorrower(ID.generate());
    const b2 = makeBorrower(ID.generate());
    wl.add(b1).add(b2);
    wl.cancel(b1);
    expect(wl.is_on_list(b1)).toBe(false);
    expect(wl.is_on_list(b2)).toBe(true);
  });

  it('process_reservation_expired clears current reservation', () => {
    const wl = new FirstComeFirstServeWaitingList({ item: makeThing() });
    const b1 = makeBorrower(ID.generate());
    wl.add(b1);
    const res = wl.reserve_item_for_next_borrower();
    expect(wl.current_reservation).toBeTruthy();
    // In our minimal TS implementation, status is not changed here, but clear_current_reservation should execute
    wl.process_reservation_expired(res);
    expect(wl.current_reservation).toBeNull();
  });
});

describe('WaitingListFactory', () => {
  it('creates FCFS or Null waiting lists', () => {
    const item = makeThing();
    const fcfs = WaitingListFactory.create_new_list({ waiting_list_type: WaitingListType.FIRST_COME_FIRST_SERVE }, item);
    expect(fcfs).toBeInstanceOf(FirstComeFirstServeWaitingList);

    const none = WaitingListFactory.create_new_list({ waiting_list_type: WaitingListType.NONE }, item);
    expect((none as WaitingList).get_reservation_time().days).toBe(0);
  });
});
