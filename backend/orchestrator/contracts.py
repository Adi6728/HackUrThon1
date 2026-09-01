from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class RiskProfile(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


class TechnicalSignal(BaseModel):
    trend: str = Field(description="Trend direction, e.g. BULLISH, BEARISH, NEUTRAL")
    strength: float = Field(default=0.0, description="Trend strength from 0.0 to 1.0")
    confidence: float = Field(default=0.0, description="Confidence score from 0.0 to 1.0")
    key_levels: Dict[str, float] = Field(default_factory=dict, description="Key support/resistance levels")
    reasoning: Optional[str] = Field(default="", description="Technical agent reasoning summary")


class SentimentSignal(BaseModel):
    polarity: str = Field(description="Sentiment polarity, e.g. POSITIVE, NEGATIVE, NEUTRAL")
    magnitude: float = Field(default=0.0, description="Sentiment score/magnitude from -1.0 to 1.0")
    headline_count: int = Field(default=0, description="Number of headlines analyzed")
    top_headlines: List[str] = Field(default_factory=list, description="Top headlines sample")
    reasoning: Optional[str] = Field(default="", description="Sentiment agent reasoning summary")


class FundamentalSignal(BaseModel):
    valuation_verdict: str = Field(description="Valuation verdict, e.g. UNDERVALUED, FAIRLY_VALUED, OVERVALUED")
    key_risks: List[str] = Field(default_factory=list, description="Key financial or business risks identified")
    citations: List[str] = Field(default_factory=list, description="RAG document excerpts or filing citations")
    reasoning: Optional[str] = Field(default="", description="Fundamental agent reasoning summary")


class SynthesizedInsight(BaseModel):
    action: str = Field(description="Recommended action, e.g. BUY, HOLD, SELL")
    confidence: float = Field(default=0.0, description="Overall confidence score from 0.0 to 1.0")
    overall_reasoning: str = Field(description="Personalized reasoning incorporating user risk profile")
    risk_caveats: List[str] = Field(default_factory=list, description="Tailored risk warnings for the investor")


class AnalysisRequest(BaseModel):
    ticker: str = Field(description="Target stock symbol, e.g. RELIANCE, TCS, AAPL")
    user_profile: RiskProfile = Field(default=RiskProfile.MODERATE, description="User risk tolerance profile")


class AnalysisResponse(BaseModel):
    ticker: str
    user_profile: str
    technical: TechnicalSignal
    sentiment: SentimentSignal
    fundamental: FundamentalSignal
    synthesized: SynthesizedInsight
    latency_ms: float = Field(default=0.0, description="Total execution time in milliseconds")
    is_degraded: bool = Field(default=False, description="Flag indicating if cached or fallback data was used")
