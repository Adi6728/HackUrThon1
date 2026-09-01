import time
import asyncio
import logging
from backend.orchestrator.contracts import (
    AnalysisRequest,
    AnalysisResponse,
    TechnicalSignal,
    SentimentSignal,
    FundamentalSignal,
    SynthesizedInsight
)
from backend.agents.technical_agent import run_technical_agent, generate_technical_signal
from backend.services.market_data.fetcher import fetch_market_snapshot
from backend.agents.sentiment_agent import run_sentiment_agent
from backend.agents.fundamental_agent import run_fundamental_agent
from backend.agents.synthesis_agent import run_synthesis_agent

logger = logging.getLogger("orchestrator.engine")


async def run_analysis(request: AnalysisRequest) -> AnalysisResponse:
    start_time = time.time()
    ticker = request.ticker.upper().strip()
    profile = request.user_profile if isinstance(request.user_profile, str) else request.user_profile.value

    # Async Parallel Agent Dispatch
    tech_task = asyncio.create_task(run_technical_agent(ticker))
    sent_task = asyncio.create_task(run_sentiment_agent(ticker))
    fund_task = asyncio.create_task(run_fundamental_agent(ticker))

    # Gather parallel agent outputs
    tech_signal, sent_signal, fund_signal = await asyncio.gather(
        tech_task, sent_task, fund_task, return_exceptions=False
    )

    # Check data degradation status from technical market snapshot if available
    is_degraded = False
    try:
        snapshot = fetch_market_snapshot(ticker)
        if snapshot and snapshot.quote:
            is_degraded = snapshot.quote.data_status in {"fallback", "cached", "unavailable"}
    except Exception:
        is_degraded = False

    # Synthesize Insights (Personalization + Conflict Resolution)
    synth_insight = await run_synthesis_agent(
        ticker, profile, tech_signal, sent_signal, fund_signal
    )

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return AnalysisResponse(
        ticker=ticker,
        user_profile=profile,
        technical=tech_signal,
        sentiment=sent_signal,
        fundamental=fund_signal,
        synthesized=synth_insight,
        latency_ms=elapsed_ms,
        is_degraded=is_degraded
    )
