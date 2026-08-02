"""Monitoring and health check endpoints"""

from fastapi import APIRouter, Depends
from datetime import datetime
import platform
import psutil

from ...core.predictor import PredictatorEngine
from ...models import DatabaseManager
from ..dependencies import get_predictator, get_db

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/health")
async def health_check(
    predictator: PredictatorEngine = Depends(get_predictator),
    db: DatabaseManager = Depends(get_db)
):
    """Comprehensive health check"""
    
    # Check database
    db_healthy = True
    try:
        db.get_all_products()
    except:
        db_healthy = False
    
    return {
        "status": "healthy" if predictator.is_trained and db_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "model": {
                "status": "healthy" if predictator.is_trained else "degraded",
                "last_training": predictator.last_training_date,
                "r2_score": predictator.training_metrics.get('r2', 0)
            },
            "database": {
                "status": "healthy" if db_healthy else "down"
            },
            "api": {
                "status": "healthy",
                "version": "2.0.0"
            }
        }
    }


@router.get("/metrics")
async def get_metrics(predictator: PredictatorEngine = Depends(get_predictator)):
    """Get model performance metrics"""
    
    if not predictator.is_trained:
        return {"error": "Model not trained yet"}
    
    return {
        "success": True,
        "model_metrics": predictator.training_metrics,
        "total_predictions": predictator.total_predictions,
        "last_training": predictator.last_training_date,
        "model_loaded": True
    }


@router.get("/system")
async def system_metrics():
    """Get system resource metrics"""
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version()
        },
        "resources": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "disk_percent": psutil.disk_usage('/').percent
        }
    }


@router.get("/predictions/stats")
async def prediction_stats(predictator: PredictatorEngine = Depends(get_predictator)):
    """Get prediction statistics"""
    
    return {
        "total_predictions": predictator.total_predictions,
        "model_ready": predictator.is_trained,
        "last_training": predictator.last_training_date,
        "model_metrics": predictator.training_metrics if predictator.is_trained else None
    }