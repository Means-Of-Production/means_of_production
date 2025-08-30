import { Borrower } from '../borrower';
import { LibraryFee } from '../libraries/library_fee';
import { Person } from './person';
import { ID, BorrowerVerificationFlags } from '../../value_items';

export class PersonBorrower extends Person implements Borrower {
  library_id: ID;
  verification_flags: BorrowerVerificationFlags[] = [];
  private _fees: LibraryFee[] = [];

  constructor(params: { person_id: ID; name: Person['name']; emails?: Person['emails']; library_id: ID; verification_flags?: BorrowerVerificationFlags[] }) {
    super({ person_id: params.person_id, name: params.name, emails: params.emails });
    this.library_id = params.library_id;
    this.verification_flags = params.verification_flags ?? [];
  }

  get fees(): ReadonlyArray<LibraryFee> {
    return this._fees;
  }

  apply_fee(fee: LibraryFee): this {
    this._fees.push(fee);
    return this;
  }
}
