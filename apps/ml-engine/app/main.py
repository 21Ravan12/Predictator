from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .core.predictor import PredictatorEngine
from .models import DatabaseManager
from .config import settings
from .api.routes.monitoring import router as monitoring_router
from .api.routes.predictions import router as predictions_router
from .api.routes.products import router as products_router
from .api.routes.training import router as training_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
predictator = PredictatorEngine()
db = DatabaseManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Predictator Engine v2.0...")
    if predictator.load_model():
        logger.info("✅ Loaded existing model")
    else:
        logger.info("⚠️ No existing model found")
    yield
    if predictator.is_trained:
        predictator.save_model()
        logger.info("💾 Model saved")

# Create FastAPI app
app = FastAPI(
    title="Predictator Engine",
    description="Retail AI Engine - Predictor + Dictator",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(monitoring_router)
app.include_router(predictions_router)
app.include_router(products_router)
app.include_router(training_router)

# ==================== ONLY ROOT & HEALTH ====================

@app.get("/")
async def root():
    return {
        "message": "🧠 Predictator Engine v2.0",
        "status": "ready",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if predictator.is_trained else "degraded",
        "model_loaded": predictator.is_trained,
        "last_training": predictator.last_training_date.isoformat() if predictator.last_training_date else None
    }

