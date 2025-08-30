import { Library } from './library';
import { Lender } from '../lenders/lender';
import { Borrower } from '../borrower';
import { Loan } from '../loan';
import { Thing } from '../thing';
import { ID, DueDate, LoanStatus, ThingStatus, ThingTitle, Location } from '../../value_items';
import { BorrowerNotInGoodStandingError, InvalidThingStatusToBorrowError } from '../../value_items/exceptions';

export class SimpleLibrary extends Library implements Lender {
  private _items: Thing[] = [];
  location: Location; // PhysicalLocation in Python, but keep generic Location interface

  get entity_id(): ID { return this.library_id; }

  add_item(item: Thing): Thing {
    this._items.push(item);
    return item;
  }

  get all_things(): Iterable<Thing> {
    return this._items;
  }

  get items(): Iterable<Thing> {
    return this._items;
  }

  async borrow(thing: Thing, borrower: Borrower, until?: DueDate | null): Promise<Loan> {
    if (thing.status !== ThingStatus.READY) {
      throw new InvalidThingStatusToBorrowError(thing.status as any);
    }
    if (!this.can_borrow(borrower)) {
      throw new BorrowerNotInGoodStandingError();
    }

    if (!until) {
      const now = new Date();
      const due = new Date(now);
      due.setDate(due.getDate() + this.default_loan_time.days);
      until = new DueDate({ date: due });
    }

    const loan = new Loan({
      loan_id: ID.generate(),
      item: thing,
      borrower_id: borrower.entity_id,
      due_date: until,
      return_location: this.location,
      time_returned: null,
    });
    loan.status = LoanStatus.BORROWED;
    thing.status = ThingStatus.BORROWED;

    this.add_loan(loan);
    return loan;
  }

  get all_titles(): Iterable<ThingTitle> {
    return Library.get_titles_from_items(this.items);
  }

  get available_titles(): Iterable<ThingTitle> {
    const available_items = Array.from(this.items).filter(i => i.status === ThingStatus.READY);
    return Library.get_titles_from_items(available_items);
  }

  get preferred_return_location(): Location {
    return this.location;
  }

  async start_return(loan: Loan): Promise<Loan> {
    loan.status = LoanStatus.RETURN_STARTED;
    loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE;
    loan.time_returned = new Date();
    return loan;
  }

  async finish_return(loan: Loan): Promise<Loan> {
    loan.status = LoanStatus.RETURNED;
    return loan;
  }
}
