from typing import List, Dict, Any
from backend.orchestrator.contracts import TechnicalSignal, SentimentSignal, FundamentalSignal

def detect_signal_conflicts(
    technical: TechnicalSignal,
    sentiment: SentimentSignal,
    fundamental: FundamentalSignal
) -> List[str]:
    """
    Identifies directional divergence between technical, sentiment, and fundamental signals.
    Returns a list of identified conflict warning strings.
    """
    conflicts = []

    tech_bullish = technical.trend.upper() == "BULLISH"
    tech_bearish = technical.trend.upper() == "BEARISH"

    sent_positive = sentiment.polarity.upper() == "POSITIVE"
    sent_negative = sentiment.polarity.upper() == "NEGATIVE"

    fund_undervalued = fundamental.valuation_verdict.upper() == "UNDERVALUED"
    fund_overvalued = fundamental.valuation_verdict.upper() == "OVERVALUED"

    # Conflict 1: Technical Bullish vs Fundamental Overvalued
    if tech_bullish and fund_overvalued:
        conflicts.append(
            "Signal Conflict Detected: Technical indicators signal bullish momentum, but fundamental analysis flags overvaluation."
        )

    # Conflict 2: Technical Bullish vs Negative News Sentiment
    if tech_bullish and sent_negative:
        conflicts.append(
            "Signal Conflict Detected: Technical indicators signal price breakout, but news sentiment is negative."
        )

    # Conflict 3: Fundamental Undervalued vs Technical Bearish
    if fund_undervalued and tech_bearish:
        conflicts.append(
            "Signal Conflict Detected: Stock is fundamentally undervalued, but price charts exhibit a bearish downtrend."
        )

    # Conflict 4: Positive Sentiment vs Bearish Technicals
    if sent_positive and tech_bearish:
        conflicts.append(
            "Signal Conflict Detected: News sentiment is positive, but price action remains in a technical downtrend."
        )

    return conflicts
