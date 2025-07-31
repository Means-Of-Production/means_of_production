import decimal

from pydantic import BaseModel

from domain.value_items import Currency, Money


class MoneyFactory(BaseModel):
    default_currency_name: Currency = Currency.EUR

    def empty(self, currency_name: Currency | None = None) -> Money:
        if not currency_name:
            currency_name = self.default_currency_name
        return Money(
            amount=decimal.Decimal(0),
            currency_name=currency_name,
        )

    def total(self, amounts: list[Money]) -> Money:
        if not amounts:
            return self.empty()
        total = self.empty(amounts[0].currency_name)
        for amount in amounts:
            total.amount += amount.amount
        return total
