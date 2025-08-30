import { Entity } from '../entity';
import { ID, PersonName, EmailAddress } from '../../value_items';

export class Person extends Entity {
  person_id: ID;
  name: PersonName;
  emails: EmailAddress[];

  constructor(params: { person_id: ID; name: PersonName; emails?: EmailAddress[] }) {
    super();
    this.person_id = params.person_id;
    this.name = params.name;
    this.emails = params.emails ?? [];
  }

  get entity_id(): ID { return this.person_id; }

  get preferred_email(): EmailAddress | null {
    if (!this.emails || this.emails.length === 0) return null;
    return this.emails[0] as EmailAddress;
  }
}
