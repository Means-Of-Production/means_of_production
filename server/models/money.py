from typing import Optional

from pydantic import BaseModel, Field

from domain import Currency

from .symbol import Symbol


class Money(BaseModel):
    amount: float = Field(..., description="Decimal amount of money")
    currency_name: Currency
    symbol: Optional[Symbol] = None
