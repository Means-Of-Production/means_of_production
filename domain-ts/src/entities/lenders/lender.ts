import { Entity } from '../entity';
import { Loan } from '../loan';
import { Thing } from '../thing';
import { Location } from '../../value_items';

export abstract class Lender extends Entity {
  abstract get items(): Iterable<Thing>;
  abstract start_return(loan: Loan): Promise<Loan>;
  abstract finish_return(loan: Loan): Promise<Loan>;
  abstract get preferred_return_location(): Location;
}
