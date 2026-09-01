import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.agents import router as agents_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("api.main")

app = FastAPI(
    title="Multi-Agent Autonomous Financial Intelligence API Gateway",
    description="API Gateway serving multi-agent stock analysis, market insights, and personalized risk intelligence.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(agents_router)


@app.get("/api/health", tags=["Health Check"])
async def health_check():
    """
    System health check endpoint verifying API gateway availability.
    """
    return {
        "status": "online",
        "system": "Multi-Agent Autonomous Financial Intelligence Gateway",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
