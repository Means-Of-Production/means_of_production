import { describe, it, expect } from 'vitest';
import { Thing } from '../../src/entities/thing';
import { ID } from '../../src/value_items/id';
import { ThingTitle } from '../../src/value_items/thing_title';
import { ThingStatus } from '../../src/value_items/thing_status';
import { PhysicalLocation } from '../../src/value_items/location/physical_location';

describe('Thing', () => {
  function makeThing(): Thing {
    return new Thing({
      thing_id: ID.generate(),
      title: new ThingTitle({ name: 'Drill' }),
      description: null,
      owner_id: ID.generate(),
      storage_location: new PhysicalLocation({ street_address: '1 Main', city: 'X', state: 'Y', zip_code: '00000', country: 'US' }),
    });
  }

  it('allows valid status transitions and rejects invalid', () => {
    const thing = makeThing();
    expect(thing.status).toBe(ThingStatus.READY);

    thing.status = ThingStatus.BORROWED;
    expect(thing.status).toBe(ThingStatus.BORROWED);

    // Invalid: BORROWED -> READY is valid, but BORROWED -> DAMAGED is allowed too; test invalid by going DAMAGED -> READY
    thing.status = ThingStatus.DAMAGED;
    expect(() => { thing.status = ThingStatus.READY; }).toThrowError();
  });
});
