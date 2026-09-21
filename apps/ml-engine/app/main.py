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

# 🆕 Import gRPC server
from .grpc.server import start_grpc_server_in_thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
predictator = PredictatorEngine()
db = DatabaseManager()

# 🆕 Global gRPC server reference
grpc_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global grpc_server
    
    # 🚀 STARTUP
    logger.info("🚀 Starting Predictator Engine v2.0...")
    
    # Load model
    if predictator.load_model():
        logger.info("✅ Loaded existing model")
    else:
        logger.info("⚠️ No existing model found")
    
    # 🆕 Start gRPC server
    try:
        logger.info("📡 Starting gRPC server on port 50051...")
        grpc_server = start_grpc_server_in_thread(port=50051)
        logger.info("✅ gRPC server started on port 50051")
    except Exception as e:
        logger.error(f"❌ Failed to start gRPC server: {e}")
    
    yield
    
    # 🛑 SHUTDOWN
    if predictator.is_trained:
        predictator.save_model()
        logger.info("💾 Model saved")
    
    # 🆕 Stop gRPC server
    if grpc_server:
        logger.info("🛑 Stopping gRPC server...")
        grpc_server.stop(grace=5)
        logger.info("✅ gRPC server stopped")

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
        "docs": "/docs",
        "grpc": "port 50051"  # 🆕 Show gRPC info
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if predictator.is_trained else "degraded",
        "model_loaded": predictator.is_trained,
        "last_training": predictator.last_training_date.isoformat() if predictator.last_training_date else None,
        "grpc_running": grpc_server is not None  # 🆕 Check gRPC status
    }
