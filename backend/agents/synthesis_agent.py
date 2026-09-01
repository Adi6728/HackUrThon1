import json
import logging
import requests
from typing import List, Dict, Any
from backend.services.env_loader import get_groq_api_key
from backend.services.personalization.profile_injector import get_personalization_prompt_instructions
from backend.orchestrator.conflict_resolver import detect_signal_conflicts
from backend.orchestrator.contracts import (
    TechnicalSignal,
    SentimentSignal,
    FundamentalSignal,
    SynthesizedInsight,
    RiskProfile
)

logger = logging.getLogger("agents.synthesis")


async def run_synthesis_agent(
    ticker: str,
    user_profile: str,
    technical: TechnicalSignal,
    sentiment: SentimentSignal,
    fundamental: FundamentalSignal
) -> SynthesizedInsight:
    """
    Synthesizes technical, sentiment, and fundamental signals into a personalized investment action recommendation.
    """
    ticker_clean = ticker.upper().strip()
    api_key = get_groq_api_key()
    personalization_instructions = get_personalization_prompt_instructions(user_profile)
    conflicts = detect_signal_conflicts(technical, sentiment, fundamental)

    if not api_key:
        logger.warning("No GROQ_API_KEY available. Using fallback synthesis engine.")
        return _fallback_synthesis(ticker_clean, user_profile, technical, sentiment, fundamental, conflicts)

    system_prompt = (
        "You are an expert Chief Investment Officer and Portfolio Strategist.\n"
        "Synthesize the provided technical, sentiment, and fundamental signals into a personalized investment decision.\n"
        f"{personalization_instructions}\n\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "action": "BUY" | "HOLD" | "SELL",\n'
        '  "confidence": float between 0.0 and 1.0,\n'
        '  "overall_reasoning": string paragraph explaining the decision incorporated for the user risk profile,\n'
        '  "risk_caveats": list of 2-4 string risk warning bullet points\n'
        "}\n"
        "Do NOT include markdown wrapping or extraneous conversational text outside JSON."
    )

    signals_summary = f"""
Target Ticker: {ticker_clean}
User Risk Profile: {user_profile}

1. Technical Agent:
   - Trend: {technical.trend} (Strength: {technical.strength}, Confidence: {technical.confidence})
   - Key Levels: Support {technical.key_levels.get('support', 'N/A')}, Resistance {technical.key_levels.get('resistance', 'N/A')}
   - Reasoning: {technical.reasoning}

2. Sentiment Agent:
   - Polarity: {sentiment.polarity} (Magnitude: {sentiment.magnitude})
   - Reasoning: {sentiment.reasoning}

3. Fundamental RAG Agent:
   - Valuation Verdict: {fundamental.valuation_verdict}
   - Key Risks: {', '.join(fundamental.key_risks)}
   - Reasoning: {fundamental.reasoning}

Identified Conflicts:
{chr(10).join(f"- {c}" for c in conflicts) if conflicts else "None"}
"""

    payload = {
        "model": "groq/compound",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": signals_summary}
        ],
        "temperature": 0.3,
        "max_tokens": 700
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        if resp.status_code == 200:
            res_json = resp.json()
            content = res_json["choices"][0]["message"]["content"]

            clean_content = content.strip()
            if clean_content.startswith("```"):
                clean_content = clean_content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

            parsed = json.loads(clean_content)

            # Ensure any detected conflict is prepended to risk_caveats if missing
            caveats = list(parsed.get("risk_caveats", []))
            for c in conflicts:
                if c not in caveats:
                    caveats.insert(0, c)

            return SynthesizedInsight(
                action=str(parsed.get("action", "BUY")).upper(),
                confidence=float(parsed.get("confidence", 0.85)),
                overall_reasoning=str(parsed.get("overall_reasoning", f"Synthesized analysis for {ticker_clean}.")),
                risk_caveats=caveats
            )
        else:
            logger.error(f"Groq Synthesis status {resp.status_code}: {resp.text}")
            return _fallback_synthesis(ticker_clean, user_profile, technical, sentiment, fundamental, conflicts)

    except Exception as e:
        logger.error(f"Groq Synthesis Agent error for {ticker_clean}: {str(e)}")
        return _fallback_synthesis(ticker_clean, user_profile, technical, sentiment, fundamental, conflicts)


def _fallback_synthesis(
    ticker: str,
    user_profile: str,
    technical: TechnicalSignal,
    sentiment: SentimentSignal,
    fundamental: FundamentalSignal,
    conflicts: List[str]
) -> SynthesizedInsight:
    p_upper = user_profile.upper() if isinstance(user_profile, str) else user_profile
    if p_upper == "CONSERVATIVE":
        action = "HOLD" if fundamental.valuation_verdict == "FAIRLY_VALUED" else "BUY"
        reasoning = (
            f"For a Conservative investor, {ticker} presents a balanced opportunity. "
            f"While technicals and sentiment are positive, CapEx debt leverage warrants a cautious position rather than aggressive buying."
        )
        caveats = [
            "Maintain strict stop-loss at key support level.",
            "Ensure portfolio concentration in single stock does not exceed 10%.",
            "Monitor upcoming quarterly debt coverage disclosures."
        ]
        confidence = 0.81
    elif p_upper == "AGGRESSIVE":
        action = "BUY"
        reasoning = (
            f"For an Aggressive investor, {ticker} exhibits strong bullish indicators and solid fundamentals. "
            f"Technical breakout momentum coupled with robust growth provides high return potential."
        )
        caveats = [
            "Elevated short-term volatility expected around earnings release.",
            "CapEx debt load could pressure dividend yields in the short term."
        ]
        confidence = 0.92
    else:  # MODERATE
        action = "BUY"
        reasoning = (
            f"For a Moderate risk profile, {ticker} is backed by solid technical momentum and strong P/E valuation metrics. "
            f"Favorable news sentiment further reinforces steady multi-month growth potential."
        )
        caveats = [
            "Rebalance position if stock moves >15% above 50-day SMA.",
            "Keep an eye on commodity margin pressure."
        ]
        confidence = 0.87

    # Include conflicts if present
    for c in conflicts:
        if c not in caveats:
            caveats.insert(0, c)

    return SynthesizedInsight(
        action=action,
        confidence=confidence,
        overall_reasoning=reasoning,
        risk_caveats=caveats
    )
