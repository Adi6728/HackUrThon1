from __future__ import annotations

import math
from typing import Sequence

from backend.services.market_data.models import IndicatorSet


def _safe_float(value):
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return numeric


def _calculate_rsi(prices: Sequence[float], period: int = 14):
    if len(prices) < 2:
        return None

    effective_period = min(period, max(1, len(prices) - 1))
    deltas = [prices[idx] - prices[idx - 1] for idx in range(1, len(prices))]
    gains = [max(delta, 0.0) for delta in deltas]
    losses = [abs(min(delta, 0.0)) for delta in deltas]

    avg_gain = sum(gains[:effective_period]) / effective_period
    avg_loss = sum(losses[:effective_period]) / effective_period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    for idx in range(effective_period, len(gains)):
        avg_gain = ((avg_gain * (effective_period - 1)) + gains[idx]) / effective_period
        avg_loss = ((avg_loss * (effective_period - 1)) + losses[idx]) / effective_period

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return max(0.0, min(100.0, rsi))


def _calculate_ema(values: Sequence[float], period: int):
    if not values:
        return None
    multiplier = 2.0 / (period + 1)
    ema = values[0]
    for value in values[1:]:
        ema = (value - ema) * multiplier + ema
    return ema


def _calculate_macd(prices: Sequence[float]):
    if len(prices) < 2:
        return None, None, None

    fast_period = min(12, max(2, len(prices) - 1))
    slow_period = min(26, max(3, len(prices)))
    signal_period = min(9, max(2, len(prices) // 2))

    ema_fast = _calculate_ema(prices[-fast_period:], fast_period)
    ema_slow = _calculate_ema(prices[-slow_period:], slow_period)
    if ema_fast is None or ema_slow is None:
        return None, None, None

    macd = ema_fast - ema_slow
    signal_values = [macd] * max(1, min(len(prices), signal_period))
    signal = _calculate_ema(signal_values, signal_period)
    histogram = None if signal is None else macd - signal
    return macd, signal, histogram


def _calculate_bollinger(prices: Sequence[float], window: int = 20):
    if len(prices) < 2:
        return None, None, None

    effective_window = min(window, len(prices))
    window_prices = list(prices[-effective_window:])
    avg = sum(window_prices) / len(window_prices)
    variance = sum((price - avg) ** 2 for price in window_prices) / len(window_prices)
    std_dev = math.sqrt(variance)
    upper = avg + (2 * std_dev)
    lower = avg - (2 * std_dev)
    return upper, avg, lower


def _calculate_vwap(prices: Sequence[float], volumes: Sequence[int] | None):
    if not prices or not volumes or len(prices) != len(volumes):
        return None

    total_volume = sum(max(int(volume), 0) for volume in volumes)
    if total_volume <= 0:
        return None

    weighted_price_sum = sum(float(price) * max(int(volume), 0) for price, volume in zip(prices, volumes))
    return weighted_price_sum / total_volume


def _calculate_obv(prices: Sequence[float], volumes: Sequence[int] | None):
    if not prices or not volumes or len(prices) != len(volumes):
        return None

    obv = 0.0
    prev_close = prices[0]
    for price, volume in zip(prices[1:], volumes[1:]):
        if price > prev_close:
            obv += float(volume)
        elif price < prev_close:
            obv -= float(volume)
        prev_close = price
    return obv


def calculate_indicator_set(prices: Sequence[float], volumes: Sequence[int] | None = None) -> IndicatorSet:
    """Calculate the most useful indicators for the existing MarketSnapshot contract.

    This function is intentionally defensive: if insufficient history or invalid values are
    present, it returns None for the unavailable indicators instead of raising exceptions.
    """
    cleaned_prices = [_safe_float(price) for price in prices]
    cleaned_prices = [price for price in cleaned_prices if price is not None]
    if not cleaned_prices:
        return IndicatorSet()

    volumes_clean = None
    if volumes is not None:
        volumes_clean = [int(v) for v in volumes if v is not None]

    rsi = _calculate_rsi(cleaned_prices)
    macd, macd_signal, macd_histogram = _calculate_macd(cleaned_prices)
    bollinger_upper, bollinger_middle, bollinger_lower = _calculate_bollinger(cleaned_prices)
    vwap = _calculate_vwap(cleaned_prices, volumes_clean)
    obv = _calculate_obv(cleaned_prices, volumes_clean) if volumes_clean else None

    sma_20 = None
    if len(cleaned_prices) >= 2:
        window_20 = min(20, len(cleaned_prices))
        sma_20 = _safe_float(sum(cleaned_prices[-window_20:]) / window_20)

    sma_50 = None
    if len(cleaned_prices) >= 2:
        window_50 = min(50, len(cleaned_prices))
        sma_50 = _safe_float(sum(cleaned_prices[-window_50:]) / window_50)

    return IndicatorSet(
        rsi=_safe_float(rsi),
        macd=_safe_float(macd),
        macd_signal=_safe_float(macd_signal),
        macd_histogram=_safe_float(macd_histogram),
        sma_20=sma_20,
        sma_50=sma_50,
        bollinger_upper=_safe_float(bollinger_upper),
        bollinger_middle=_safe_float(bollinger_middle),
        bollinger_lower=_safe_float(bollinger_lower),
        vwap=_safe_float(vwap),
        obv=_safe_float(obv),
    )


__all__ = ["calculate_indicator_set"]
