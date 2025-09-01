import { Library } from './library';
import { Borrower } from '../borrower';
import { Loan } from '../loan';
import { Thing } from '../thing';
import { Lender } from '../lenders/lender';
import { ID, DueDate, LoanStatus, PhysicalArea, ThingStatus } from '../../value_items';

export class DistributedLibrary extends Library {
  area!: PhysicalArea;
  private _lenders: Lender[] = [];

  get entity_id(): ID { return this.library_id; }

  get all_things(): Iterable<Thing> {
    const items: Thing[] = [];
    for (const lender of this._lenders) {
      for (const thing of lender.items) items.push(thing);
    }
    return items;
  }

  get_owner_of_item(item: Thing): Lender {
    for (const lender of this._lenders) {
      for (const lender_item of lender.items) {
        if (item.entity_id && lender_item.entity_id && item.entity_id.equals(lender_item.entity_id)) {
          return lender;
        }
      }
    }
    throw new Error(`Cannot find an owner for ${item.title.name}`);
  }

  async borrow(thing: Thing, borrower: Borrower, until?: DueDate | null): Promise<Loan> {
    if (thing.status !== ThingStatus.READY) {
      throw new Error(String(thing.status));
    }
    if (!this.can_borrow(borrower)) {
      throw new Error('BorrowerNotInGoodStandingError');
    }

    const lender = this.get_owner_of_item(thing);
    if (!lender) throw new Error(`Cannot find owner of item ${thing.entity_id}`);

    if (!until) {
      const now = new Date();
      const due = new Date(now);
      due.setDate(due.getDate() + this.default_loan_time.days);
      until = new DueDate({ date: due });
    }

    thing.status = ThingStatus.BORROWED;

    const loan = new Loan({
      loan_id: ID.generate(),
      item: thing,
      borrower_id: borrower.entity_id,
      due_date: until,
      return_location: lender.preferred_return_location,
      time_returned: null,
    });
    loan.status = LoanStatus.BORROWED;
    return loan;
  }

  async finish_library_return(loan: Loan, borrower: Borrower): Promise<Loan> {
    const owner = this.get_owner_of_item(loan.item);
    const from_owner = await owner.finish_return(loan);
    return super.finish_library_return(from_owner, borrower);
  }

  async start_return(loan: Loan): Promise<Loan> {
    const owner = this.get_owner_of_item(loan.item);
    const updated = await owner.start_return(loan);

    loan.time_returned = new Date();
    if (updated.status !== LoanStatus.WAITING_ON_LENDER_ACCEPTANCE) {
      updated.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE;
    }
    return updated;
  }

  add_lender(lender: Lender): Lender {
    this._lenders.push(lender);
    return lender;
  }
}
