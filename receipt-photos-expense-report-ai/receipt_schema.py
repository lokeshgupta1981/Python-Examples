"""The fields we want from every receipt."""
import datetime
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["meals", "lodging", "transport", "supplies", "other"]


class Receipt(BaseModel):
    merchant: str | None = Field(description="Shop, restaurant or company name")
    date: datetime.date | None = Field(description="Purchase date as YYYY-MM-DD")
    currency: str | None = Field(description="Three-letter code such as EUR, GBP or USD")
    amount_before_tax: float | None = Field(description="The Net or Subtotal line")
    tax: float | None = Field(description="VAT, MwSt or sales tax amount")
    tip: float | None = Field(description="Tip or service charge, 0 if none")
    total: float | None = Field(description="Final amount paid")
    card_last4: str | None = Field(description="Last four digits of the card")
    category: Category
