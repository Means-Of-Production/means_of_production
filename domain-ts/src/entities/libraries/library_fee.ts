import { Entity } from '../entity';
import { ID, FeeStatus, Money } from '../../value_items';

export class LibraryFee extends Entity {
  library_fee_id: ID;
  library_id: ID;
  amount: Money;
  private _status: FeeStatus = FeeStatus.OUTSTANDING;
  charged_for_id: ID;

  constructor(params: { library_fee_id: ID; library_id: ID; amount: Money; charged_for_id: ID }) {
    super();
    this.library_fee_id = params.library_fee_id;
    this.library_id = params.library_id;
    this.amount = params.amount;
    this.charged_for_id = params.charged_for_id;
  }

  get status(): FeeStatus { return this._status; }
  set status(value: FeeStatus) { this._status = value; }

  get entity_id(): ID { return this.library_fee_id; }
}
