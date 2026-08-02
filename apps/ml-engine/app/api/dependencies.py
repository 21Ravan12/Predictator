"""Dependency injection for API routes"""

from fastapi import Request, HTTPException
from typing import Optional

from ..core.predictor import PredictatorEngine
from ..models import DatabaseManager
from ..core.dictator import DictatorEngine

# Singleton instances
_predictator = None
_db = None
_dictator = None


def get_predictator() -> PredictatorEngine:
    """Get Predictator engine instance"""
    global _predictator
    if _predictator is None:
        _predictator = PredictatorEngine()
        _predictator.load_model()
    return _predictator


def get_db() -> DatabaseManager:
    """Get database instance"""
    global _db
    if _db is None:
        _db = DatabaseManager()
    return _db


def get_dictator() -> DictatorEngine:
    """Get Dictator engine instance"""
    global _dictator
    if _dictator is None:
        _dictator = DictatorEngine()
    return _dictator


async def validate_product(product_id: str, db: DatabaseManager = None):
    """Validate product exists"""
    if db is None:
        db = get_db()
    
    history = db.load_sales_history(product_id, days_back=1)
    if history.empty:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product_id


async def validate_training_data(csv_path: Optional[str] = None):
    """Validate training data source"""
    if not csv_path:
        return True
    
    import os
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=400, detail=f"CSV file not found: {csv_path}")
    return True