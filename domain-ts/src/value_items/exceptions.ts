import { ReservationStatus } from './reservation_status';
import { ThingStatus } from './thing_status';

export class CurrencyMismatchException extends Error {
  constructor(message?: string) {
    super(message ?? 'Currency mismatch');
    this.name = 'CurrencyMismatchException';
  }
}

export class InvalidThingStateTransitionError extends Error {
  public readonly current_status: ThingStatus;
  public readonly new_status: ThingStatus;
  constructor(current_status: ThingStatus, new_status: ThingStatus) {
    const message = `Invalid thing state transition. Current status: ${current_status}, New status: ${new_status}`;
    super(message);
    this.name = 'InvalidThingStateTransitionError';
    this.current_status = current_status;
    this.new_status = new_status;
  }
}

export class InvalidReservationStateTransitionError extends Error {
  public readonly current_status: ReservationStatus;
  public readonly new_status: ReservationStatus;
  constructor(current_status: ReservationStatus, new_status: ReservationStatus) {
    const message = `Invalid reservation state transition. Current status: ${current_status}, New status: ${new_status}`;
    super(message);
    this.name = 'InvalidReservationStateTransitionError';
    this.current_status = current_status;
    this.new_status = new_status;
  }
}

export class ReturnNotStartedError extends Error {
  constructor(message?: string) {
    super(message ?? 'Return not started');
    this.name = 'ReturnNotStartedError';
  }
}

export class ConflictingKeyException extends Error {
  constructor(message?: string) {
    super(message ?? 'Conflicting key');
    this.name = 'ConflictingKeyException';
  }
}

export class ResourceNotFoundException extends Error {
  constructor(message?: string) {
    super(message ?? 'Resource not found');
    this.name = 'ResourceNotFoundException';
  }
}

export class EntityNotAssignedIdError extends Error {
  constructor(message?: string) {
    super(message ?? 'Entity not assigned ID');
    this.name = 'EntityNotAssignedIdError';
  }
}

export class InvalidThingStatusToBorrowError extends Error {
  constructor(status: ThingStatus) {
    super(String(status));
    this.name = 'InvalidThingStatusToBorrowError';
  }
}

export class BorrowerNotInGoodStandingError extends Error {
  constructor(message?: string) {
    super(message ?? 'Borrower not in good standing');
    this.name = 'BorrowerNotInGoodStandingError';
  }
}

export class InvalidLibraryConfigurationError extends Error {
  constructor(message?: string) {
    super(message ?? 'Invalid library configuration');
    this.name = 'InvalidLibraryConfigurationError';
  }
}
