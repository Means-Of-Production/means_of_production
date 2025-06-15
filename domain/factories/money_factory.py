from domain.value_items import Money


class MoneyFactory:
    @staticmethod
    def empty(currency_name: str) -> Money:
        return Money(
            amount=0,
            currency_name=currency_name,
        )

    @staticmethod
    def total(amounts: list[Money]) -> Money:
        total = MoneyFactory.empty(amounts[0].currency_name)
        for amount in amounts:
            total.amount += amount.amount
        return total
