"""API routes module"""

from .predictions import router as predictions_router
from .training import router as training_router
from .products import router as products_router
from .monitoring import router as monitoring_router

__all__ = [
    'predictions_router',
    'training_router',
    'products_router',
    'monitoring_router'
]