"""Training endpoints"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional

from ...models import TrainRequest, TrainResponse
from ...core.predictor import PredictatorEngine
from ...models import DatabaseManager
from ..dependencies import get_predictator, get_db, validate_training_data

router = APIRouter(prefix="/train", tags=["Training"])


@router.post("", response_model=TrainResponse)
async def train_model(
    request: Optional[TrainRequest] = None,
    background_tasks: BackgroundTasks = None,
    predictator: PredictatorEngine = Depends(get_predictator),
    db: DatabaseManager = Depends(get_db)
):
    """Train or retrain the prediction model"""
    
    if predictator.is_trained and not (request and request.force_retrain):
        return TrainResponse(
            success=True,
            message="Model already trained. Use force_retrain=true to retrain",
            samples_used=0,
            metrics=predictator.training_metrics
        )
    
    try:
        # Load data
        if request and request.csv_path:
            import pandas as pd
            df = pd.read_csv(request.csv_path, parse_dates=['date'])
        else:
            df = predictator.generate_sample_data()

        # Train
        metrics = predictator.train(df)
        predictator.save_model()
        
        # Save sample to DB
        if len(df) > 0 and 'sample_product' not in [p[0] for p in db.get_all_products()]:
            db.save_sales_history(df)
        
        return TrainResponse(
            success=True,
            message="Model trained successfully!",
            samples_used=len(df),
            metrics=metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def training_status(predictator: PredictatorEngine = Depends(get_predictator)):
    """Get training status"""
    return {
        "is_trained": predictator.is_trained,
        "last_training": predictator.last_training_date,
        "metrics": predictator.training_metrics,
        "model_path": "model.pkl"
    }


@router.post("/retrain")
async def retrain_model(
    csv_path: Optional[str] = None,
    predictator: PredictatorEngine = Depends(get_predictator)
):
    """Force model retraining"""
    from ...models import TrainRequest
    request = TrainRequest(csv_path=csv_path, force_retrain=True)
    return await train_model(request, None, predictator)