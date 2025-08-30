import Decimal from 'decimal.js';
import { CurrencyMismatchException } from './exceptions';

export enum Currency {
  EUR = 'Euro',
  USD = 'US Dollar',
  HOUR = 'Labor Token',
}

export class Money {
  public readonly amount: Decimal;
  public readonly currency: Currency;
  public readonly symbol?: string;

  constructor(params: { amount: Decimal.Value; currency: Currency; symbol?: string | null }) {
    this.amount = new Decimal(params.amount);
    this.currency = params.currency;
    this.symbol = params.symbol ?? undefined;
  }

  get dollars(): Decimal {
    if (this.currency !== Currency.USD) {
      throw new CurrencyMismatchException('Can only convert to dollars if currency is USD');
    }
    return this.amount;
  }

  equals(other: unknown): boolean {
    if (!(other instanceof Money)) return false;
    return this.currency === other.currency && this.amount.eq(other.amount);
  }

  greaterThan(other: Money): boolean {
    this.ensureSameCurrency(other);
    return this.amount.gt(other.amount);
  }

  greaterThanOrEqual(other: Money): boolean {
    this.ensureSameCurrency(other);
    return this.amount.gte(other.amount);
  }

  lessThan(other: Money): boolean {
    this.ensureSameCurrency(other);
    return this.amount.lt(other.amount);
  }

  lessThanOrEqual(other: Money): boolean {
    this.ensureSameCurrency(other);
    return this.amount.lte(other.amount);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new CurrencyMismatchException('Can only add Money objects with the same currency');
    }
    return new Money({ amount: this.amount.plus(other.amount), currency: this.currency, symbol: this.symbol });
  }

  mul(multiplier: number): Money {
    return new Money({ amount: this.amount.mul(multiplier), currency: this.currency, symbol: this.symbol });
  }

  private ensureSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new CurrencyMismatchException();
    }
  }

  toJSON(): { amount: string; currency: Currency; symbol?: string } {
    const json: { amount: string; currency: Currency; symbol?: string } = {
      amount: this.amount.toString(),
      currency: this.currency,
    };
    if (this.symbol) json.symbol = this.symbol;
    return json;
  }
}
