"""Training endpoints"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
import pandas as pd
from pathlib import Path
import logging

from ...models import TrainRequest, TrainResponse
from ...core.predictor import PredictatorEngine
from ...models import DatabaseManager
from ..dependencies import get_predictator, get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/train", tags=["Training"])

ML_ENGINE_ROOT = Path(__file__).resolve().parents[3]

# 🆕 Dataset paths (in priority order)
LARGE_DATASET = ML_ENGINE_ROOT / "data/raw/sales_data_large.csv"
HOLIDAYS_CSV = ML_ENGINE_ROOT / "data/raw/holidays_baku.csv"
PRODUCTS_CSV = ML_ENGINE_ROOT / "data/raw/products.csv"
CATEGORIES_CSV = ML_ENGINE_ROOT / "data/raw/categories.csv"


def resolve_training_csv(csv_path: str) -> Optional[Path]:
    """Resolve request paths from the working directory or the ML-engine root."""
    requested_path = Path(csv_path).expanduser()
    candidates = (
        [requested_path]
        if requested_path.is_absolute()
        else [requested_path, ML_ENGINE_ROOT / requested_path]
    )

    if requested_path.as_posix().removeprefix("./") == "data/historical-sales.csv":
        candidates.append(ML_ENGINE_ROOT / "data/legacy/historical-sales.csv")

    return next((path for path in candidates if path.is_file()), None)


@router.post("", response_model=TrainResponse)
async def train_model(
    request: Optional[TrainRequest] = None,
    background_tasks: BackgroundTasks = None,
    predictator: PredictatorEngine = Depends(get_predictator),
    db: DatabaseManager = Depends(get_db),
):
    """Train or retrain the prediction model"""

    if predictator.is_trained and not (request and request.force_retrain):
        return TrainResponse(
            success=True,
            message="Model already trained. Use force_retrain=true to retrain",
            samples_used=0,
            metrics=predictator.training_metrics or {},
        )

    try:
        # ============================================
        # 📥 LOAD DATA (priority order)
        # ============================================
        if request and request.csv_path:
            csv_path = resolve_training_csv(request.csv_path)
            if csv_path is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"CSV not found: {request.csv_path}",
                )
            df = pd.read_csv(csv_path, parse_dates=['date'])
            logger.info(f"📊 Loaded from request: {csv_path} ({len(df):,} rows)")

        elif LARGE_DATASET.exists():
            df = pd.read_csv(LARGE_DATASET, parse_dates=['date'])
            logger.info(f"📊 Loaded large dataset: {len(df):,} rows")
            logger.info(f"📦 Products: {df['product_id'].nunique()}")

        else:
            logger.warning(f"⚠️ Large dataset not found at {LARGE_DATASET}")
            logger.info("📊 Falling back to sample data")
            df = predictator.generate_sample_data()

        # ============================================
        # 🎓 TRAIN MODEL
        # ============================================
        metrics = predictator.train(df)

        if not metrics:
            raise HTTPException(
                status_code=500,
                detail="Training failed - no metrics returned",
            )

        predictator.save_model()

        # ============================================
        # 💾 SAVE TO DATABASE
        # ============================================
        if len(df) > 0:
            try:
                db.save_sales_history(df)
                logger.info(f"✅ Saved {len(df):,} sales records to database")
            except Exception as e:
                logger.error(f"⚠️ Failed to save to DB: {e}")
                # Don't fail training if DB save fails

        # ============================================
        # 📦 SAVE PRODUCTS (if available)
        # ============================================
        if PRODUCTS_CSV.exists():
            try:
                products_df = pd.read_csv(PRODUCTS_CSV)
                db.save_products(products_df)
                logger.info(f"✅ Saved {len(products_df)} products")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save products: {e}")

        # ============================================
        # 📁 SAVE CATEGORIES (if available)
        # ============================================
        if CATEGORIES_CSV.exists():
            try:
                categories_df = pd.read_csv(CATEGORIES_CSV)
                db.save_categories(categories_df)
                logger.info(f"✅ Saved {len(categories_df)} categories")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save categories: {e}")

        # ============================================
        # 🎉 SAVE HOLIDAYS
        # ============================================
        if HOLIDAYS_CSV.exists():
            try:
                holidays_df = pd.read_csv(HOLIDAYS_CSV, parse_dates=['date'])
                holidays_df = holidays_df.dropna(subset=['holiday_name'])

                if not holidays_df.empty:
                    db.save_holidays_to_bank(holidays_df)
                    logger.info(f"✅ Saved {len(holidays_df)} holidays")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save holidays: {e}")

        # ============================================
        # ✅ RETURN RESPONSE
        # ============================================
        return TrainResponse(
            success=True,
            message="Model trained successfully!",
            samples_used=len(df),
            metrics=metrics,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Training error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def training_status(predictator: PredictatorEngine = Depends(get_predictator)):
    """Get training status"""
    return {
        "is_trained": predictator.is_trained,
        "last_training": predictator.last_training_date,
        "metrics": predictator.training_metrics,
        "model_path": "model.pkl",
        "n_features": len(predictator.feature_columns) if predictator.feature_columns else 0,
    }


@router.post("/retrain")
async def retrain_model(
    csv_path: Optional[str] = None,
    predictator: PredictatorEngine = Depends(get_predictator),
    db: DatabaseManager = Depends(get_db),
):
    """Force model retraining"""
    from ...models import TrainRequest
    request = TrainRequest(csv_path=csv_path, force_retrain=True)
    return await train_model(request, None, predictator, db)
