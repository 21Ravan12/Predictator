"""API module - routes and dependencies"""

from .dependencies import get_predictator, get_db, get_dictator
from .routes import predictions, training, products, monitoring

__all__ = [
    'get_predictator',
    'get_db', 
    'get_dictator',
    'predictions',
    'training',
    'products',
    'monitoring'
]