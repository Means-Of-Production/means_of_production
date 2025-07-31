from typing import Optional

from pydantic import BaseModel, Field

from .currency_name import CurrencyName
from .symbol import Symbol


class Money(BaseModel):
    amount: float = Field(..., description='Decimal amount of money')
    currency_name: CurrencyName
    symbol: Optional[Symbol] = None