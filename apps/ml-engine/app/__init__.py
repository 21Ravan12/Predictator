"""Predictator ML Engine - Core AI components"""

from .core.predictor import PredictatorEngine
from .core.dictator import DictatorEngine
from .models import DatabaseManager
from .models import (
    PredictRequest,
    PredictResponse,
    TrainRequest,
    TrainResponse,
    HealthResponse,
    SinglePrediction
)

__all__ = [
    'PredictatorEngine',
    'DatabaseManager',
    'PredictRequest',
    'PredictResponse',
    'TrainRequest',
    'TrainResponse',
    'HealthResponse',
    'SinglePrediction'
]

__version__ = '2.0.0'