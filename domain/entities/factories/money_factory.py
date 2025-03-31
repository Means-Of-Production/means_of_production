from domain.value_items.money import Money
from domain.value_items.money import USDMoney


class MoneyFactory:
    """
    Factory class for creating money objects.
    """

    def __init__(self, money_type: str = "USDMoney"):
        self.money_type = money_type

    def get_empty_money(self) -> Money:
        """Returns an instance of money with zero value."""
        if self.money_type == "USDMoney":
            return USDMoney(0)
        raise ValueError(f"Invalid money type: {self.money_type}")

    def total(self, items: list[Money]) -> Money:
        """Calculates the total sum of all money objects in the iterable."""
        result = self.get_empty_money()
        for item in items:
            result = result.add(item)
        return result
