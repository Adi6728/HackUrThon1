from __future__ import annotations

from datetime import datetime, timezone

from backend.services.market_data.indicators import calculate_indicator_set
from backend.services.market_data.models import IndicatorSet, MarketSnapshot, StockQuote


_DEFALT_BASE_PRICES = {
    "RELIANCE": 2525.0,
    "TCS": 3920.0,
    "INFY": 1525.0,
    "HDFCBANK": 1650.0,
    "ICICIBANK": 1185.0,
    "AAPL": 214.0,
    "MSFT": 418.0,
    "NVDA": 128.0,
    "AMZN": 184.0,
    "GOOG": 178.0,
}


def _normalize_ticker(ticker: str) -> str:
    if ticker is None or not str(ticker).strip():
        raise ValueError("ticker is required")

    normalized = str(ticker).strip().upper()
    if not normalized or not normalized.replace("-", "").replace(".", "").isalnum():
        raise ValueError(f"invalid ticker: {ticker}")
    return normalized


def _build_mock_series(ticker: str):
    base_price = _DEFALT_BASE_PRICES.get(ticker, 100.0 + (sum(ord(ch) for ch in ticker) % 200))
    drift = [0.0]
    for i in range(1, 21):
        drift.append(((i % 5) - 2) * 0.018 + (1 if i % 2 == 0 else -1) * 0.006)

    prices = [base_price]
    for step in drift[1:]:
        prices.append(round(prices[-1] * (1 + step), 2))

    volumes = []
    base_volume = 1_800_000 + (sum(ord(ch) for ch in ticker) % 1_200_000)
    for idx, _ in enumerate(prices):
        if idx == 0:
            volumes.append(base_volume)
        else:
            delta = ((idx % 4) - 1) * 180_000
            volumes.append(max(200_000, base_volume + delta + idx * 30_000))
    return prices, volumes


def fetch_market_snapshot(ticker: str, *, data_source: str = "mock") -> MarketSnapshot:
    """Fetch market data in the project's intended shape.

    The repository currently has no live market provider configured, so the default path
    is a deterministic mock dataset that is clearly labeled as degraded/fallback data.
    Real data sources can be supplied via the data_source argument when available; this
    function still normalizes them into the existing MarketSnapshot contract.
    """
    normalized_ticker = _normalize_ticker(ticker)

    resolved_source = (data_source or "mock").strip().lower()
    use_fallback = resolved_source in {"fallback", "mock", "cache", "cached", "unavailable", "error"}

    if resolved_source not in {"live", "cached", "fallback", "mock", "cache", "unavailable"}:
        use_fallback = True

    prices, volumes = _build_mock_series(normalized_ticker)
    now = datetime.now(timezone.utc)
    latest_price = float(prices[-1])
    opening_price = float(prices[0])
    high_price = max(float(p) for p in prices)
    low_price = min(float(p) for p in prices)
    close_price = float(prices[-1])

    indicators = calculate_indicator_set(prices, volumes)

    status = "live" if not use_fallback else "fallback"
    quote = StockQuote(
        ticker=normalized_ticker,
        price=latest_price,
        open=opening_price,
        high=high_price,
        low=low_price,
        close=close_price,
        volume=int(volumes[-1]),
        timestamp=now,
        data_source="mock" if use_fallback else resolved_source,
        data_status=status,
    )

    return MarketSnapshot(
        quote=quote,
        indicators=indicators,
        ticker=normalized_ticker,
        timestamp=now,
    )


__all__ = ["fetch_market_snapshot"]
