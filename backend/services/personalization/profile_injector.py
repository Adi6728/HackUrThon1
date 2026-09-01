from typing import Dict, Any, List
from backend.orchestrator.contracts import RiskProfile
from backend.services.user_profile.store import get_user_profile_config

def get_personalization_prompt_instructions(user_profile: str) -> str:
    """
    Generates LLM system prompt directives based on user risk profile.
    """
    p_config = get_user_profile_config(user_profile)
    p_name = p_config["label"].upper()
    max_alloc = p_config["max_single_stock_allocation_pct"]
    stop_loss = p_config["stop_loss_pct"]
    capex_sens = p_config["capex_debt_sensitivity"]

    if p_name == "CONSERVATIVE":
        return (
            "USER RISK PROFILE: CONSERVATIVE.\n"
            "- Prioritize capital preservation and drawdown minimization over speculative gains.\n"
            "- If fundamental valuation is OVERVALUED or risk indicators (debt/CapEx) are HIGH, favor 'HOLD' or 'SELL'.\n"
            f"- Mandate strict risk caveats: max single stock allocation {max_alloc}%, strict stop-loss at {stop_loss}%.\n"
            "- Highlight CapEx debt leverage and financial stability warnings in caveats."
        )
    elif p_name == "AGGRESSIVE":
        return (
            "USER RISK PROFILE: AGGRESSIVE.\n"
            "- Prioritize capital growth, technical breakout momentum, and market expansion potential.\n"
            "- If technical trend or sentiment is strong, favor 'BUY' even if valuation is slightly elevated.\n"
            f"- Mandate growth-oriented risk caveats: position cap at {max_alloc}%, stop-loss at {stop_loss}%.\n"
            "- Focus warnings on short-term volatility and earnings announcements."
        )
    else:  # MODERATE
        return (
            "USER RISK PROFILE: MODERATE.\n"
            "- Balance multi-month capital growth against risk management.\n"
            "- Weigh technical momentum against fundamental valuation metrics evenly.\n"
            f"- Provide practical risk caveats: position cap at {max_alloc}%, stop-loss at {stop_loss}%."
        )
