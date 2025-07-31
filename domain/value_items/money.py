from __future__ import annotations

import decimal
from enum import Enum

from pydantic import BaseModel

from domain.value_items.exceptions import CurrencyMismatchException


class Currency(Enum):
    EUR = "Euro"
    USD = "US Dollar"
    HOUR = "Labor Token"


class Money(BaseModel):
    model_config = {"frozen": True}
    amount: decimal.Decimal
    currency: Currency
    symbol: str | None = None

    @property
    def dollars(self) -> decimal.Decimal:
        if self.currency != Currency.USD:
            raise CurrencyMismatchException(
                "Can only convert to dollars if currency is USD"
            )
        return self.amount

    def __eq__(self, other):
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __gt__(self, other: Money) -> bool:
        if self.currency != other.currency:
            raise CurrencyMismatchException()
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        if self.currency != other.currency:
            raise CurrencyMismatchException()
        return self.amount >= other.amount

    def __lt__(self, other: Money) -> bool:
        if self.currency != other.currency:
            raise CurrencyMismatchException()
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        if self.currency != other.currency:
            raise CurrencyMismatchException()
        return self.amount <= other.amount

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                "Can only add Money objects with the same currency"
            )

        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __mul__(self, other: int | float) -> Money:
        return Money(
            amount=self.amount * decimal.Decimal(other),
            currency=self.currency,
        )
