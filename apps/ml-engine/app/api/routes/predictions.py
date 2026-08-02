"""Prediction endpoints"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime

from ...models import PredictRequest, PredictResponse
from ...core.predictor import PredictatorEngine
from ...core.dictator import DictatorEngine
from ...models import DatabaseManager
from ..dependencies import get_predictator, get_db, get_dictator

router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("", response_model=PredictResponse)
async def create_predictions(
    request: PredictRequest,
    background_tasks: BackgroundTasks,
    predictator: PredictatorEngine = Depends(get_predictator),
    dictator: DictatorEngine = Depends(get_dictator),
    db: DatabaseManager = Depends(get_db)
):
    """Generate sales predictions with dictator enforcement"""
    
    if not predictator.is_trained:
        raise HTTPException(status_code=400, detail="Model not trained. Call POST /train first")

    # Load history
    history = db.load_sales_history(request.product_id, days_back=90)
    if len(history) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Need 30+ days of history. Only have {len(history)}"
        )
    
    # Generate predictions
    predictions, conf_intervals, _ = predictator.predict(
        days_ahead=request.days_ahead,
        last_sales=history
    )
    
    # Apply dictator rules
    context = {
        'floor_limit': request.floor_limit,
        'current_stock': history['sales'].tail(7).mean()
    }
    
    final_predictions = []
    alerts = []
    
    for i, (pred, conf) in enumerate(zip(predictions, conf_intervals)):
        final, alert = predictator.enforce_floor_limit(pred, request.floor_limit)
        final_predictions.append(final)
        if alert:
            alerts.append({"day": i+1, "message": alert})
    
    # Prepare response
    future_dates = [
        (datetime.now().replace(hour=0, minute=0, second=0) + __import__('datetime').timedelta(days=i+1)).strftime("%Y-%m-%d")
        for i in range(request.days_ahead)
    ]
    
    prediction_list = [
        {
            "date": date,
            "predicted_sales": round(final_predictions[i], 2),
            "confidence_lower": round(conf_intervals[i][0], 2),
            "confidence_upper": round(conf_intervals[i][1], 2),
            "alert": alerts[i]["message"] if i < len(alerts) else None
        }
        for i, date in enumerate(future_dates)
    ]
    
    # Log in background
    background_tasks.add_task(
        db.log_prediction,
        request.product_id,
        prediction_list,
        request.floor_limit
    )
    
    predictator.total_predictions += len(prediction_list)
    
    return PredictResponse(
        product_id=request.product_id,
        predictions=prediction_list,
        summary={
            "total_predicted": sum(p["predicted_sales"] for p in prediction_list),
            "average_daily": sum(p["predicted_sales"] for p in prediction_list) / len(prediction_list),
            "peak_day": max(p["predicted_sales"] for p in prediction_list),
            "floor_violations": len(alerts)
        },
        dictator_actions=alerts,  # ← List of dicts! ✅
        alerts=[a["message"] for a in alerts]  # ← List of strings! ✅
    )

@router.post("/bulk")
async def bulk_predictions(
    product_ids: List[str],
    days_ahead: int = 7,
    floor_limit: int = 0,
    predictator: PredictatorEngine = Depends(get_predictator),
    db: DatabaseManager = Depends(get_db)
):
    """Get predictions for multiple products"""
    
    results = {}
    for product_id in product_ids:
        try:
            history = db.load_sales_history(product_id, days_back=90)
            if len(history) >= 30:
                preds, _, _ = predictator.predict(days_ahead, history)
                final_preds = [max(p, floor_limit) if floor_limit > 0 else p for p in preds]
                results[product_id] = {
                    "predictions": [round(p, 2) for p in final_preds],
                    "total": sum(final_preds)
                }
            else:
                results[product_id] = {"error": f"Only {len(history)} days of history"}
        except Exception as e:
            results[product_id] = {"error": str(e)}
    
    return {
        "success": True,
        "products": results,
        "total_units": sum(r.get("total", 0) for r in results.values())
    }


@router.get("/health")
async def prediction_health(predictator: PredictatorEngine = Depends(get_predictator)):
    """Check prediction service health"""
    return {
        "status": "healthy" if predictator.is_trained else "degraded",
        "model_loaded": predictator.is_trained,
        "total_predictions": predictator.total_predictions,
        "last_training": predictator.last_training_date
    }