import asyncio
from datetime import datetime
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.market_data.models import IndicatorSet, MarketSnapshot, StockQuote
from backend.services.market_data.fetcher import fetch_market_snapshot
from backend.services.market_data.indicators import calculate_indicator_set
from backend.agents.technical_agent import generate_technical_signal
from backend.orchestrator.contracts import AnalysisRequest
from backend.orchestrator.engine import run_analysis


def test_valid_stock_quote():
    quote = StockQuote(
        ticker="AAPL",
        price=101.25,
        open=100.5,
        high=102.0,
        low=99.75,
        close=101.0,
        volume=1250000,
        timestamp=datetime(2026, 9, 1, 12, 0, 0),
        data_source="yfinance",
        data_status="live",
    )

    assert quote.ticker == "AAPL"
    assert quote.price == 101.25
    assert quote.close == 101.0
    assert quote.data_status == "live"


def test_invalid_negative_price():
    with pytest.raises(ValidationError):
        StockQuote(
            ticker="MSFT",
            price=-10.0,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=5000,
            timestamp=datetime(2026, 9, 1, 12, 0, 0),
            data_source="yfinance",
            data_status="live",
        )


def test_invalid_negative_volume():
    with pytest.raises(ValidationError):
        StockQuote(
            ticker="MSFT",
            price=100.0,
            open=99.0,
            high=101.0,
            low=98.0,
            close=100.5,
            volume=-1,
            timestamp=datetime(2026, 9, 1, 12, 0, 0),
            data_source="yfinance",
            data_status="cached",
        )


def test_valid_market_snapshot():
    quote = StockQuote(
        ticker="NVDA",
        price=200.0,
        open=198.0,
        high=201.0,
        low=197.0,
        close=199.5,
        volume=2000000,
        timestamp=datetime(2026, 9, 1, 12, 0, 0),
        data_source="yfinance",
        data_status="fallback",
    )
    indicators = IndicatorSet(
        rsi=58.5,
        macd=1.2,
        macd_signal=0.8,
        macd_histogram=0.4,
        sma_20=195.5,
        sma_50=190.0,
        bollinger_upper=205.0,
        bollinger_middle=198.0,
        bollinger_lower=191.0,
        vwap=198.75,
        obv=4500000.0,
    )

    snapshot = MarketSnapshot(
        quote=quote,
        indicators=indicators,
        ticker="NVDA",
        timestamp=quote.timestamp,
    )

    assert snapshot.quote.ticker == "NVDA"
    assert snapshot.indicators.rsi == 58.5
    assert snapshot.timestamp == quote.timestamp


def test_market_snapshot_with_missing_indicators():
    quote = StockQuote(
        ticker="TSLA",
        price=220.0,
        open=218.0,
        high=221.0,
        low=216.0,
        close=219.5,
        volume=3200000,
        timestamp=datetime(2026, 9, 1, 12, 0, 0),
        data_source="cache",
        data_status="cached",
    )

    snapshot = MarketSnapshot(
        quote=quote,
        indicators=IndicatorSet(),
        ticker="TSLA",
        timestamp=quote.timestamp,
    )

    assert snapshot.indicators.rsi is None
    assert snapshot.indicators.macd is None
    assert snapshot.indicators.sma_20 is None


def test_market_snapshot_json_serialization():
    quote = StockQuote(
        ticker="AMZN",
        price=170.0,
        open=169.2,
        high=171.5,
        low=168.8,
        close=170.25,
        volume=1500000,
        timestamp=datetime(2026, 9, 1, 12, 0, 0),
        data_source="yfinance",
        data_status="live",
    )
    snapshot = MarketSnapshot(
        quote=quote,
        indicators=IndicatorSet(),
        ticker="AMZN",
        timestamp=quote.timestamp,
    )

    payload = snapshot.model_dump(mode="json")
    assert payload["ticker"] == "AMZN"
    assert payload["quote"]["ticker"] == "AMZN"
    assert payload["quote"]["timestamp"] == "2026-09-01T12:00:00"

    json_payload = snapshot.model_dump_json()
    assert '"ticker":"AMZN"' in json_payload
    assert '"data_status":"live"' in json_payload


def test_invalid_required_fields():
    with pytest.raises(ValidationError):
        StockQuote(
            ticker="",
            price=100.0,
            open=99.0,
            high=101.0,
            low=98.5,
            close=100.5,
            volume=1000,
            timestamp=datetime(2026, 9, 1, 12, 0, 0),
            data_source="yfinance",
            data_status="live",
        )

    with pytest.raises(ValidationError):
        MarketSnapshot(
            quote=None,
            indicators=IndicatorSet(),
            ticker="GOOG",
            timestamp=datetime(2026, 9, 1, 12, 0, 0),
        )


def test_indicator_calculation_robustness():
    prices = [100.0, 101.0, 102.5, 101.5, 103.0, 104.0, 106.0, 102.0]
    volumes = [2000, 2100, 2200, 2150, 2400, 2500, 2600, 2300]
    indicators = calculate_indicator_set(prices, volumes)

    assert isinstance(indicators, IndicatorSet)
    assert indicators.rsi is not None
    assert indicators.macd is not None
    assert indicators.bollinger_upper is not None
    assert indicators.vwap is not None
    assert indicators.obv is not None


def test_technical_agent_generates_signal_from_snapshot():
    quote = StockQuote(
        ticker="RELIANCE",
        price=2550.0,
        open=2480.0,
        high=2570.0,
        low=2460.0,
        close=2545.0,
        volume=3200000,
        timestamp=datetime(2026, 9, 1, 12, 0, 0),
        data_source="fallback",
        data_status="fallback",
    )
    snapshot = MarketSnapshot(
        quote=quote,
        indicators=IndicatorSet(
            rsi=62.0,
            macd=1.5,
            macd_signal=0.8,
            macd_histogram=0.7,
            sma_20=2520.0,
            sma_50=2480.0,
            bollinger_upper=2590.0,
            bollinger_middle=2520.0,
            bollinger_lower=2450.0,
            vwap=2515.0,
            obv=25000000.0,
        ),
        ticker="RELIANCE",
        timestamp=quote.timestamp,
    )

    signal = generate_technical_signal(snapshot)

    assert signal.trend in {"BULLISH", "BEARISH", "NEUTRAL"}
    assert 0.0 <= signal.confidence <= 1.0
    assert signal.key_levels
    assert signal.reasoning


def test_run_analysis_uses_market_data_and_technical_signal():
    request = AnalysisRequest(ticker="RELIANCE", user_profile="MODERATE")
    response = asyncio.run(run_analysis(request))

    assert response.ticker == "RELIANCE"
    assert response.technical.trend in {"BULLISH", "BEARISH", "NEUTRAL"}
    assert isinstance(response.technical.key_levels, dict)
    assert response.technical.reasoning


def test_fetch_market_snapshot_returns_market_snapshot():
    snapshot = fetch_market_snapshot("RELIANCE")

    assert isinstance(snapshot, MarketSnapshot)
    assert snapshot.quote.ticker == "RELIANCE"
    assert snapshot.indicators is not None
    assert snapshot.ticker == "RELIANCE"
