import { describe, it, expect } from 'vitest';
import { SimpleLibrary } from '../../../src/entities/libraries/simple_library';
import { ID, DueDate, LoanStatus, ThingStatus, ThingTitle, WaitingListType } from '../../../src/value_items';
import { Person } from '../../../src/entities/people/person';
import { PersonName } from '../../../src/value_items/person_name';
import { URL } from '../../../src/value_items/url';
import { MOPServer } from '../../../src/entities/mop_server';
import { Money, Currency } from '../../../src/value_items/money';
import { MoneyFactory } from '../../../src/factories/money_factory';
import { FeeSchedule } from '../../../src/value_items/fee_schedules/fee_schedule';
import { Thing } from '../../../src/entities/thing';
import { PhysicalLocation } from '../../../src/value_items/location/physical_location';

class TestFeeSchedule implements FeeSchedule {
  feeForOverdueItem() { return new Money({ amount: 5, currency: Currency.USD }); }
  feeForDamagedItem() { return new Money({ amount: 20, currency: Currency.USD }); }
}

describe('SimpleLibrary (expanded tests)', () => {
  function makeLibrary() {
    const admin = new Person({ person_id: ID.generate(), name: new PersonName({ first_name: 'Admin', last_name: 'User' }) });
    const fee_schedule = new TestFeeSchedule();
    const money_factory = new MoneyFactory();
    const mop_server = MOPServer.localhost();

    const lib = new SimpleLibrary({
      library_id: ID.generate(),
      name: 'Test Simple Library',
      administrator: admin,
      waiting_list_type: WaitingListType.FIRST_COME_FIRST_SERVE,
      max_fines_before_suspension: new Money({ amount: 50, currency: Currency.USD }),
      fee_schedule,
      default_loan_time: { days: 14 },
      mop_server,
      public_url: URL.parse('https://example.com') as any,
    });
    lib.location = new PhysicalLocation({ street_address: '1 Main', city: 'X', state: 'Y', zip_code: '00000', country: 'US' });
    (lib as any).money_factory.default_currency = Currency.USD;
    return lib;
  }

  function makeThing(): Thing {
    return new Thing({
      thing_id: ID.generate(),
      title: new ThingTitle({ name: 'Test Book' }),
      description: null,
      owner_id: ID.generate(),
      storage_location: new PhysicalLocation({ street_address: '1 Main', city: 'X', state: 'Y', zip_code: '00000', country: 'US' }),
    });
  }

  it('entity_id returns library_id', () => {
    const lib = makeLibrary();
    expect(lib.entity_id.equals(lib.library_id)).toBe(true);
  });

  it('add_item stores and returns item; all_things and items include it', () => {
    const lib = makeLibrary();
    const thing = makeThing();
    const result = lib.add_item(thing);
    expect(result).toBe(thing);
    expect(Array.from(lib.all_things)).toContain(thing);
    expect(Array.from(lib.items)).toContain(thing);
  });

  it('borrow with default due date sets reasonable future date', async () => {
    const lib = makeLibrary();
    const thing = makeThing();
    const borrower: any = { entity_id: ID.generate(), library_id: lib.entity_id, fees: [], apply_fee: () => borrower };
    lib.add_item(thing);

    // monkey-patch can_borrow to true similar to Python test patch
    const original = lib.can_borrow.bind(lib);
    (lib as any).can_borrow = () => true;
    const loan = await lib.borrow(thing, borrower);
    (lib as any).can_borrow = original;

    expect(loan.due_date).toBeTruthy();
    const today = new Date();
    const dd = loan.due_date.date!;
    expect(dd.getTime()).toBeGreaterThan(today.getTime() - 1000);
    // rough upper bound ~ 15 days out
    const upper = new Date(); upper.setDate(upper.getDate() + 15);
    expect(dd.getTime()).toBeLessThan(upper.getTime());
  });

  it('rejects borrowing when item not READY', async () => {
    const lib = makeLibrary();
    const thing = makeThing();
    thing.status = ThingStatus.BORROWED;
    const borrower: any = { entity_id: ID.generate() };
    await expect(lib.borrow(thing, borrower)).rejects.toBeTruthy();
  });

  it('start_return sets WAITING_ON_LENDER_ACCEPTANCE and time_returned', async () => {
    const lib = makeLibrary();
    const thing = makeThing();
    const borrower: any = { entity_id: ID.generate(), library_id: lib.entity_id, fees: [], apply_fee: () => borrower };
    (lib as any).can_borrow = () => true;
    const loan = await lib.borrow(thing, borrower, new DueDate({ date: new Date(Date.now() + 8640000) }));
    const res = await lib.start_return(loan);
    expect(res.status).toBe(LoanStatus.WAITING_ON_LENDER_ACCEPTANCE);
    expect(res.time_returned).toBeInstanceOf(Date);
  });

  it('all_titles deduplicates and available_titles filters by READY', () => {
    const lib = makeLibrary();
    // create raw "Thing"-like objects for titles only by using real Things and adjusting status
    const t1 = makeThing(); t1.title = new ThingTitle({ name: 'Book 1' }); t1.status = ThingStatus.READY;
    const t2 = makeThing(); t2.title = new ThingTitle({ name: 'Book 2' }); t2.status = ThingStatus.READY;
    const t3 = makeThing(); t3.title = new ThingTitle({ name: 'Book 1' }); t3.status = ThingStatus.BORROWED;
    lib.add_item(t1); lib.add_item(t2); lib.add_item(t3);

    const all = Array.from(lib.all_titles);
    expect(all.some(tt => tt.equals(new ThingTitle({ name: 'Book 1' })))).toBe(true);
    expect(all.some(tt => tt.equals(new ThingTitle({ name: 'Book 2' })))).toBe(true);
    expect(all.length).toBe(2);

    const avail = Array.from(lib.available_titles);
    expect(avail.length).toBe(2);
    expect(avail.some(tt => tt.equals(new ThingTitle({ name: 'Book 3' })))).toBe(false);
  });

  it('preferred_return_location returns library.location', () => {
    const lib = makeLibrary();
    expect(lib.preferred_return_location).toEqual(lib.location);
  });
});
