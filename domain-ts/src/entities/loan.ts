import { Entity } from './entity';
import { Thing } from './thing';
import { ID, DueDate, LoanStatus, Location } from '../value_items';

export class Loan extends Entity {
  loan_id: ID;
  item: Thing;
  due_date: DueDate;
  borrower_id: ID;
  location: Location | null;
  private _status: LoanStatus = LoanStatus.RETURNED;
  return_location: Location;
  time_returned: Date | null;

  constructor(params: {
    loan_id: ID;
    item: Thing;
    due_date: DueDate;
    borrower_id: ID;
    location?: Location | null;
    return_location: Location;
    time_returned: Date | null;
  }) {
    super();
    this.loan_id = params.loan_id;
    this.item = params.item;
    this.due_date = params.due_date;
    this.borrower_id = params.borrower_id;
    this.location = params.location ?? null;
    this.return_location = params.return_location;
    this.time_returned = params.time_returned;
  }

  get lender_id(): ID {
    return this.item.owner_id;
  }

  get entity_id(): ID {
    return this.loan_id;
  }

  get active(): boolean {
    return this._status === LoanStatus.BORROWED;
  }

  get status(): LoanStatus {
    if (this.due_date && !this.due_date.isAfterNow() && this._status === LoanStatus.BORROWED) {
      this._status = LoanStatus.OVERDUE;
    }
    return this._status;
  }

  set status(value: LoanStatus) {
    let valid_new_statuses: LoanStatus[] = [];
    switch (this._status) {
      case LoanStatus.RETURNED:
        valid_new_statuses = [LoanStatus.BORROWED];
        break;
      case LoanStatus.BORROWED:
        valid_new_statuses = [LoanStatus.RETURN_STARTED, LoanStatus.OVERDUE];
        break;
      case LoanStatus.OVERDUE:
        valid_new_statuses = [LoanStatus.RETURN_STARTED];
        break;
      case LoanStatus.RETURN_STARTED:
        valid_new_statuses = [
          LoanStatus.WAITING_ON_LENDER_ACCEPTANCE,
          LoanStatus.RETURNED,
          LoanStatus.RETURNED_DAMAGED,
        ];
        break;
      case LoanStatus.WAITING_ON_LENDER_ACCEPTANCE:
        valid_new_statuses = [
          LoanStatus.RETURNED,
          LoanStatus.RETURNED_DAMAGED,
          LoanStatus.OVERDUE,
        ];
        break;
      case LoanStatus.RETURNED_DAMAGED:
      case LoanStatus.RETURNED:
        valid_new_statuses = [];
        break;
    }

    if (!valid_new_statuses.includes(value)) {
      throw new Error(`Cannot change loan status from '${this._status}' to '${value}'.`);
    }
    this._status = value;
  }

  get is_permanent_loan(): boolean {
    return this.due_date.date === null;
  }
}
