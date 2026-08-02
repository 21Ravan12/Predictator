"""Configuration management"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # App
    APP_NAME: str = "Predictator Engine"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///predictator.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # ML Settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model.pkl")
    FORECAST_DAYS: int = int(os.getenv("FORECAST_DAYS", "30"))
    
    # Dictator Settings
    DEFAULT_FLOOR_LIMIT: int = int(os.getenv("DEFAULT_FLOOR_LIMIT", "100"))
    SAFETY_STOCK_DAYS: int = int(os.getenv("SAFETY_STOCK_DAYS", "7"))
    
    # APIs
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    CALENDAR_API_KEY: str = os.getenv("CALENDAR_API_KEY", "")
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()