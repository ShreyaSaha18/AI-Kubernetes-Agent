from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from core.config import settings
from api.investigation import router as investigation_router
from api.auth import router as auth_router
from api.clusters import router as clusters_router

app = FastAPI(
    title="AI Kubernetes Agent",
    description="On-demand AI troubleshooting for Kubernetes",
    version="0.1.0"
)

logger.remove()
logger.add(sys.stdout, format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(investigation_router)
app.include_router(auth_router)
app.include_router(clusters_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-kubernetes-agent"
    }

@app.get("/")
async def root():
    return {"message": "AI Kubernetes Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
