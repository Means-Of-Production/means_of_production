import { Money } from '../money';

export interface FeeSchedule {
  feeForOverdueItem(loan: unknown): Money;
  feeForDamagedItem?(loan: unknown): Money;
}
