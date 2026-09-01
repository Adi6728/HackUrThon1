from typing import Dict, Any
from backend.orchestrator.contracts import RiskProfile

DEFAULT_PROFILES: Dict[str, Dict[str, Any]] = {
    RiskProfile.CONSERVATIVE.value: {
        "label": "Conservative",
        "description": "Capital preservation & steady yields with minimal drawdown exposure.",
        "max_single_stock_allocation_pct": 10.0,
        "stop_loss_pct": 5.0,
        "capex_debt_sensitivity": "HIGH",
        "required_confidence_threshold": 0.80,
    },
    RiskProfile.MODERATE.value: {
        "label": "Moderate",
        "description": "Balanced growth and risk management for steady multi-month gains.",
        "max_single_stock_allocation_pct": 20.0,
        "stop_loss_pct": 10.0,
        "capex_debt_sensitivity": "MEDIUM",
        "required_confidence_threshold": 0.70,
    },
    RiskProfile.AGGRESSIVE.value: {
        "label": "Aggressive",
        "description": "Capital appreciation seeking momentum and high risk-adjusted return targets.",
        "max_single_stock_allocation_pct": 35.0,
        "stop_loss_pct": 18.0,
        "capex_debt_sensitivity": "LOW",
        "required_confidence_threshold": 0.60,
    }
}


def get_user_profile_config(profile_name: str) -> Dict[str, Any]:
    p_upper = profile_name.upper().strip() if profile_name else RiskProfile.MODERATE.value
    return DEFAULT_PROFILES.get(p_upper, DEFAULT_PROFILES[RiskProfile.MODERATE.value])
