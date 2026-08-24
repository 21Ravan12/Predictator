import os

from app.core.predictor import PredictatorEngine


def test_predictor_exposes_load_model_method():
    engine = PredictatorEngine()
    assert hasattr(engine, "load_model")
    assert callable(engine.load_model)
    assert isinstance(engine.load_model(), bool)
