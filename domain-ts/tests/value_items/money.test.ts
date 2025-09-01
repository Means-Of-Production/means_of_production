import { describe, it, expect } from 'vitest';
import { Currency, Money } from '../../src/value_items/money';
import { MoneyFactory } from '../../src/factories/money_factory';

describe('Money and MoneyFactory', () => {
  it('adds same-currency amounts', () => {
    const a = new Money({ amount: 5, currency: Currency.USD });
    const b = new Money({ amount: 7.5, currency: Currency.USD });
    const c = a.add(b);
    expect(c.currency).toBe(Currency.USD);
    expect(c.amount.toNumber()).toBeCloseTo(12.5);
  });

  it('total sums array of Money', () => {
    const mf = new MoneyFactory();
    const amounts = [
      new Money({ amount: 1, currency: Currency.EUR }),
      new Money({ amount: 2, currency: Currency.EUR }),
      new Money({ amount: 3.5, currency: Currency.EUR }),
    ];
    const total = mf.total(amounts);
    expect(total.currency).toBe(Currency.EUR);
    expect(total.amount.toNumber()).toBeCloseTo(6.5);
  });
});
