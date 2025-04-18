from __future__ import annotations

from pydantic import BaseModel
from domain.value_items.exceptions import CurrencyMismatchException


class Money(BaseModel):
    """
    Represents a generic money object with an amount, currency name, and symbol.
    """

    amount: float
    currency_name: str
    symbol: str

    model_config = {"frozen": True}

    @property
    def dollars(self) -> float:
        """Returns the amount in dollars if the currency is USD."""
        if self.currency_name != "USD":
            raise CurrencyMismatchException(
                "Can only convert to dollars if currency is USD"
            )
        return self.amount

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return False

        """Checks equality based on amount and currency."""
        if other.currency_name != self.currency_name:
            return False
        return self.amount == other.amount and self.currency_name == other.currency_name

    def add(self, other: Money) -> Money:
        """
        Adds two USDMoney instances and returns a new instance.
        """
        if other.currency_name != self.currency_name:
            raise CurrencyMismatchException("Cannot add different currency types.")
        return USDMoney(self.amount + other.amount)

class USDMoney(Money):
    """
    Represents a Money instance specifically in USD.
    """

    def __init__(self, amount: float):
        super().__init__(amount=amount, currency_name="USD", symbol="$")

    def multiply(self, factor: float) -> "USDMoney":
        """
        Multiplies the amount by a factor and returns a new USDMoney instance.
        """
        return USDMoney(self.amount * factor)
