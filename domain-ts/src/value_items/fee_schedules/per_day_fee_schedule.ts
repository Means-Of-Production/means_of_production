import { Money } from '../money';
import { FeeSchedule } from './fee_schedule';

export class PerDayFeeSchedule implements FeeSchedule {
  public readonly daily_charge: Money;

  constructor(params: { daily_charge: Money }) {
    this.daily_charge = params.daily_charge;
  }

  feeForOverdueItem(loan: any): Money {
    const dueDate: Date | null | undefined = loan?.due_date?.date ?? loan?.due_date ?? null;
    if (!dueDate) {
      // zero in the same currency
      return new Money({ amount: 0, currency: this.daily_charge.currency });
    }
    const today = new Date();
    const days = Math.floor((this.stripTime(today).getTime() - this.stripTime(dueDate).getTime()) / (24 * 60 * 60 * 1000));
    const overdueDays = Math.max(0, days);
    return this.daily_charge.mul(overdueDays);
  }

  private stripTime(d: Date): Date {
    return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  }
}
