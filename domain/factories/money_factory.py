import decimal

from domain.value_items import Money


class MoneyFactory:
    @staticmethod
    def empty(currency_name: str) -> Money:
        return Money(
            amount=decimal.Decimal(0),
            currency_name=currency_name,
        )

    @staticmethod
    def total(amounts: list[Money]) -> Money:
        if not amounts:
            raise ValueError("Cannot create total of empty list")
        total = MoneyFactory.empty(amounts[0].currency_name)
        for amount in amounts:
            total.amount += amount.amount
        return total
