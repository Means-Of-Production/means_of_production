import { Entity } from '../entity';
import { Borrower } from '../borrower';
import { LibraryFee } from './library_fee';
import { Loan } from '../loan';
import { MOPServer } from '../mop_server';
import { Person } from '../people/person';
import { Thing } from '../thing';
import { WaitingList } from '../waiting_lists/waiting_list';
import { MoneyFactory, WaitingListFactory } from '../../factories';
import {
  ID,
  DueDate,
  FeeSchedule,
  FeeStatus,
  LoanStatus,
  Money,
  ThingStatus,
  ThingTitle,
  WaitingListType,
} from '../../value_items';

export abstract class Library extends Entity {
  library_id: ID;
  name: string;
  administrator: Person;
  waiting_list_type: WaitingListType;
  waiting_lists_by_item_id: Map<string, WaitingList> = new Map();
  max_fines_before_suspension: Money;
  fee_schedule: FeeSchedule;
  money_factory: MoneyFactory = new MoneyFactory();
  default_loan_time: { days: number };
  mop_server: MOPServer;
  public_url?: string | null;

  protected _borrowers: Borrower[] = [];
  protected _loans: Loan[] = [];

  constructor(params: {
    library_id: ID;
    name: string;
    administrator: Person;
    waiting_list_type: WaitingListType;
    max_fines_before_suspension: Money;
    fee_schedule: FeeSchedule;
    default_loan_time: { days: number };
    mop_server: MOPServer;
    public_url?: string | null;
  }) {
    super();
    this.library_id = params.library_id;
    this.name = params.name;
    this.administrator = params.administrator;
    this.waiting_list_type = params.waiting_list_type;
    this.max_fines_before_suspension = params.max_fines_before_suspension;
    this.fee_schedule = params.fee_schedule;
    this.default_loan_time = params.default_loan_time;
    this.mop_server = params.mop_server;
    this.public_url = params.public_url ?? null;
  }

  get entity_id(): ID {
    return this.library_id;
  }

  abstract get all_things(): Iterable<Thing>;

  get available_things(): Iterable<Thing> {
    const result: Thing[] = [];
    for (const thing of this.all_things) {
      if (thing.status === ThingStatus.READY) result.push(thing);
    }
    return result;
  }

  abstract borrow(thing: Thing, borrower: Borrower, until: DueDate): Promise<Loan>;
  abstract start_return(loan: Loan): Promise<Loan>;

  get borrowers(): Iterable<Borrower> { return this._borrowers; }

  add_borrower(borrower: Borrower): Borrower {
    this._borrowers.push(borrower);
    return borrower;
  }

  can_borrow(borrower: Borrower): boolean {
    if (!borrower.library_id || !borrower.library_id.equals(this.entity_id)) return false;

    const fee_amounts = Array.from(borrower.fees)
      .filter(f => f.status === FeeStatus.OUTSTANDING)
      .map(f => f.amount);
    const total_fees = this.money_factory.total(fee_amounts);
    return total_fees.lessThanOrEqual(this.max_fines_before_suspension);
  }

  async reserve_item(item: Thing, borrower: Borrower): Promise<WaitingList> {
    if (!item.entity_id) {
      throw new Error('EntityNotAssignedIdError');
    }
    const key = item.entity_id.toString();
    let waiting_list = this.waiting_lists_by_item_id.get(key);
    if (!waiting_list) {
      waiting_list = WaitingListFactory.create_new_list(this, item);
      this.waiting_lists_by_item_id.set(key, waiting_list);
    }
    waiting_list.add(borrower);
    return waiting_list;
  }

  get_loans(): Iterable<Loan> { return this._loans; }
  add_loan(loan: Loan): void { this._loans.push(loan); }

  static get_titles_from_items(items: Iterable<Thing>): Iterable<ThingTitle> {
    const titles: ThingTitle[] = [];
    for (const item of items) {
      if (!titles.some(t => t.equals(item.title))) titles.push(item.title);
    }
    return titles;
  }

  async finish_library_return(loan: Loan, borrower: Borrower): Promise<Loan> {
    if (loan.status !== LoanStatus.WAITING_ON_LENDER_ACCEPTANCE || !loan.time_returned) {
      throw new Error('ReturnNotStartedError');
    }

    if (loan.item.status === ThingStatus.DAMAGED) {
      loan.status = LoanStatus.RETURNED_DAMAGED;
    } else {
      if (loan.due_date) {
        if (loan.time_returned > (loan.due_date.date ?? loan.time_returned)) {
          loan.status = LoanStatus.OVERDUE;
        } else {
          loan.status = LoanStatus.RETURNED;
        }
      } else {
        loan.status = LoanStatus.RETURNED;
      }
    }

    let fee_amount: Money | null = null;
    if (loan.item.status === ThingStatus.DAMAGED) {
      // prefer camelCase per FeeSchedule interface; fall back if implementation uses snake_case
      const calculator = (this.fee_schedule as any).feeForDamagedItem ?? (this.fee_schedule as any).fee_for_damaged_item;
      if (calculator) fee_amount = calculator.call(this.fee_schedule, loan);
    }
    if (loan.status === LoanStatus.OVERDUE) {
      const calculator = (this.fee_schedule as any).feeForOverdueItem ?? (this.fee_schedule as any).fee_for_overdue_item;
      if (calculator) fee_amount = calculator.call(this.fee_schedule, loan);
    }

    if (fee_amount) {
      const fee = new LibraryFee({
        library_fee_id: ID.generate(),
        library_id: this.library_id,
        amount: fee_amount,
        charged_for_id: loan.loan_id,
      });
      fee.status = FeeStatus.OUTSTANDING;
      borrower.apply_fee(fee);
    }

    const itemIdStr = loan.item.entity_id?.toString();
    if (!itemIdStr) throw new Error('EntityNotAssignedIdError');

    const waiting_list = this.waiting_lists_by_item_id.get(itemIdStr);
    if (waiting_list) {
      waiting_list.reserve_item_for_next_borrower();
    }

    if (loan.item.status === ThingStatus.BORROWED) {
      loan.item.status = ThingStatus.READY;
    }

    return loan;
  }
}
