import { describe, it, expect } from 'vitest';
import { DistributedLibrary } from '../../../src/entities/libraries/distributed_library';
import { SimpleLibrary } from '../../../src/entities/libraries/simple_library';
import { Thing } from '../../../src/entities/thing';
import { Loan } from '../../../src/entities/loan';
import { ID } from '../../../src/value_items/id';
import { ThingTitle } from '../../../src/value_items/thing_title';
import { PhysicalLocation } from '../../../src/value_items/location/physical_location';
import { PhysicalArea } from '../../../src/value_items/location/physical_area';
import { Distance } from '../../../src/value_items/location/distance';
import { Person } from '../../../src/entities/people/person';
import { PersonName } from '../../../src/value_items/person_name';
import { URL } from '../../../src/value_items/url';
import { MOPServer } from '../../../src/entities/mop_server';
import { Money, Currency } from '../../../src/value_items/money';
import { MoneyFactory } from '../../../src/factories/money_factory';
import { FeeSchedule } from '../../../src/value_items/fee_schedules/fee_schedule';
import { WaitingListType } from '../../../src/value_items/waiting_list_types';
import { LoanStatus } from '../../../src/value_items/loan_status';
import { ThingStatus } from '../../../src/value_items/thing_status';
import { DueDate } from '../../../src/value_items/due_date';

class TestFeeSchedule implements FeeSchedule {
  feeForOverdueItem() { return new Money({ amount: 0, currency: Currency.USD }); }
  feeForDamagedItem() { return new Money({ amount: 0, currency: Currency.USD }); }
}

function makePerson(name: string) {
  return new Person({ person_id: ID.generate(), name: new PersonName({ first_name: name, last_name: 'Admin' }) });
}

function makeSimpleLibrary(name: string) {
  const lib = new SimpleLibrary({
    library_id: ID.generate(),
    name,
    administrator: makePerson(name),
    waiting_list_type: WaitingListType.FIRST_COME_FIRST_SERVE,
    max_fines_before_suspension: new Money({ amount: 100, currency: Currency.USD }),
    fee_schedule: new TestFeeSchedule(),
    default_loan_time: { days: 14 },
    mop_server: MOPServer.localhost(),
    public_url: URL.parse('https://example.com') as any,
  });
  lib.location = new PhysicalLocation({ street_address: '1 Main', city: 'X', state: 'Y', zip_code: '00000', country: 'US' });
  (lib as any).money_factory.default_currency = Currency.USD;
  return lib;
}

function makeDistributedLibrary() {
  const dl = new DistributedLibrary({
    library_id: ID.generate(),
    name: 'Distributed',
    administrator: makePerson('Dist'),
    waiting_list_type: WaitingListType.FIRST_COME_FIRST_SERVE,
    max_fines_before_suspension: new Money({ amount: 100, currency: Currency.USD }),
    fee_schedule: new TestFeeSchedule(),
    default_loan_time: { days: 7 },
    mop_server: MOPServer.localhost(),
    public_url: URL.parse('https://distributed.example') as any,
  });
  (dl as any).money_factory.default_currency = Currency.USD;
  dl.area = new PhysicalArea({ center_point: new PhysicalLocation({ street_address: '1 Center', city: 'X', state: 'Y', zip_code: '00000', country: 'US' }), radius: new Distance(50) });
  return dl;
}

function makeThing(owner_id: ID): Thing {
  return new Thing({
    thing_id: ID.generate(),
    title: new ThingTitle({ name: 'Ladder' }),
    description: null,
    owner_id,
    storage_location: new PhysicalLocation({ street_address: '2 Main', city: 'X', state: 'Y', zip_code: '00000', country: 'US' }),
  });
}

describe('DistributedLibrary', () => {
  it('aggregates lender items and borrows via owning lender', async () => {
    const dl = makeDistributedLibrary();
    const lender1 = makeSimpleLibrary('L1');
    const lender2 = makeSimpleLibrary('L2');
    dl.add_lender(lender1);
    dl.add_lender(lender2);

    const thing = makeThing(lender1.library_id);
    lender1.add_item(thing);

    const borrower: any = { entity_id: ID.generate(), library_id: dl.entity_id, fees: [], apply_fee: () => borrower };

    const until = new DueDate({ date: new Date(Date.now() + 3 * 86400000) });
    const loan = await dl.borrow(thing, borrower, until);

    expect(loan.status).toBe(LoanStatus.BORROWED);
    expect(thing.status).toBe(ThingStatus.BORROWED);
    // return_location should be owner's preferred_return_location (lender1)
    expect(loan.return_location).toEqual(lender1.preferred_return_location);
  });

  it('start_return delegates to owner and marks waiting on acceptance', async () => {
    const dl = makeDistributedLibrary();
    const lender = makeSimpleLibrary('L1');
    dl.add_lender(lender);
    const thing = makeThing(lender.library_id);
    lender.add_item(thing);

    const borrower: any = { entity_id: ID.generate(), library_id: dl.entity_id, fees: [], apply_fee: () => borrower };
    const loan = await dl.borrow(thing, borrower, new DueDate({ date: new Date(Date.now() + 86400000) }));

    const updated = await dl.start_return(loan);
    expect(updated.status).toBe(LoanStatus.WAITING_ON_LENDER_ACCEPTANCE);
    expect(loan.time_returned).toBeInstanceOf(Date);
  });
});
