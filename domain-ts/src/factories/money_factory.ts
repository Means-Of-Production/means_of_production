import { Currency, Money } from '../value_items/money';

export class MoneyFactory {
  default_currency: Currency = Currency.EUR;

  empty(currency_name?: Currency | null): Money {
    const c = currency_name ?? this.default_currency;
    return new Money({ amount: 0, currency: c });
  }

  total(amounts: Money[]): Money {
    if (!amounts || amounts.length === 0) return this.empty();
    return amounts.reduce((acc, cur) => acc.add(cur), this.empty(amounts[0].currency));
  }
}
