import { Entity } from './entity';
import { LibraryFee } from './libraries/library_fee';
import { ID, BorrowerVerificationFlags } from '../value_items';

export abstract class Borrower extends Entity {
  library_id!: ID;
  verification_flags!: BorrowerVerificationFlags[];

  abstract get fees(): ReadonlyArray<LibraryFee>;
  abstract apply_fee(fee: LibraryFee): this;
}
