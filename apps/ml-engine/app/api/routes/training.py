"""Training endpoints"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
import pandas as pd
from pathlib import Path

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
            metrics=predictator.training_metrics or {}
        )
    
    try:
        # Load sales data
        if request and request.csv_path:
            df = pd.read_csv(request.csv_path, parse_dates=['date'])
        else:
            df = predictator.generate_sample_data()

        # 🆕 Train model with error handling
        metrics = predictator.train(df)
        
        # 🆕 Check if metrics is None or empty
        if not metrics:
            raise HTTPException(
                status_code=500, 
                detail="Training failed - no metrics returned. Check logs for details."
            )
        
        predictator.save_model()
        
        # Save sales to DB
        if len(df) > 0:
            db.save_sales_history(df)
            print(f"✅ Saved {len(df)} sales records to database")
        
        # Load holidays from CSV
        holidays_csv_path = Path("data/holidays.csv")
        if holidays_csv_path.exists():
            holidays_df = pd.read_csv(holidays_csv_path, parse_dates=['date'])
            holidays_df = holidays_df.dropna(subset=['holiday_name'])
            if not holidays_df.empty:
                db.save_holidays_to_bank(holidays_df)
                print(f"✅ Loaded {len(holidays_df)} holidays from {holidays_csv_path}")
        
        # Load seasons from CSV
        seasons_csv_path = Path("data/seasons.csv")
        if seasons_csv_path.exists():
            seasons_df = pd.read_csv(seasons_csv_path, parse_dates=['start_date', 'end_date'])
            if not seasons_df.empty:
                db.save_seasons_to_bank(seasons_df)
                print(f"✅ Loaded {len(seasons_df)} seasons from {seasons_csv_path}")
        
        # 🆕 Return response with metrics
        return TrainResponse(
            success=True,
            message="Model trained successfully!",
            samples_used=len(df),
            metrics=metrics  # ← This should NOT be None!
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in training: {e}")
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