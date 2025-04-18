from pydantic import BaseModel

from domain.value_items.exceptions import CurrencyMismatchException


class Money(BaseModel):
    model_config = {"frozen": True}
    amount: float
    currency_name: str
    symbol: str | None = None

    @property
    def dollars(self) -> float:
        if not self.currency_name == "USD":
            raise CurrencyMismatchException(
                "Can only convert to dollars if currency is USD"
            )
        return self.amount

    def __eq__(self, other):
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency_name == other.currency_name
