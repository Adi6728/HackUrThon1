import logging
from fastapi import APIRouter, HTTPException, status
from backend.orchestrator.contracts import AnalysisRequest, AnalysisResponse
from backend.orchestrator import engine

logger = logging.getLogger("api.routes.agents")
router = APIRouter(prefix="/api", tags=["Agents & Analysis"])


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_stock(request: AnalysisRequest) -> AnalysisResponse:
    """
    Trigger full multi-agent analysis for a given stock ticker and user risk profile.
    Returns technical, sentiment, fundamental, and synthesized investment insights.
    """
    if not request.ticker or not request.ticker.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock ticker symbol cannot be empty."
        )

    try:
        response = await engine.run_analysis(request)
        return response
    except Exception as e:
        logger.error(f"Error during multi-agent analysis for ticker {request.ticker}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute multi-agent analysis: {str(e)}"
        )
