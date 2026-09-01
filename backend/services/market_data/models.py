from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


DataStatus = Literal["live", "cached", "fallback", "unavailable"]


class StockQuote(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    ticker: str = Field(..., min_length=1, max_length=20)
    price: float = Field(..., gt=0)
    open: float | None = Field(default=None, gt=0)
    high: float | None = Field(default=None, gt=0)
    low: float | None = Field(default=None, gt=0)
    close: float = Field(..., gt=0)
    volume: int | None = Field(default=None, ge=0)
    timestamp: datetime
    data_source: str = Field(..., min_length=1)
    data_status: DataStatus

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized or not normalized.replace("-", "").replace(".", "").isalnum():
            raise ValueError("ticker must be a valid stock symbol")
        return normalized


class IndicatorSet(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    sma_20: float | None = None
    sma_50: float | None = None
    bollinger_upper: float | None = None
    bollinger_middle: float | None = None
    bollinger_lower: float | None = None
    vwap: float | None = None
    obv: float | None = None


class MarketSnapshot(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    quote: StockQuote
    indicators: IndicatorSet
    ticker: str = Field(..., min_length=1, max_length=20)
    timestamp: datetime

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized or not normalized.replace("-", "").replace(".", "").isalnum():
            raise ValueError("ticker must be a valid stock symbol")
        return normalized

    @model_validator(mode="after")
    def ensure_quote_matches_ticker(self) -> "MarketSnapshot":
        if self.quote.ticker.upper() != self.ticker.upper():
            raise ValueError("quote.ticker must match the snapshot ticker")
        return self
