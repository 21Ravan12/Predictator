"""Weather Connector - CSV-based learning implementation

Currently loads weather data from a local CSV file to learn real-world
data formats. Later, will switch to a real API (OpenWeatherMap).

The interface stays the same: swap `_load_csv()` for `_fetch_api()`
and everything else keeps working.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# ============================================
# 📦 DATA STRUCTURE
# ============================================

@dataclass
class WeatherData:
    """Weather data structure (matches future API response)"""
    date: datetime
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    condition: str
    precipitation: float
    is_extreme: bool


# ============================================
# 🌤️ CONNECTOR
# ============================================

class WeatherConnector:
    """Weather connector - CSV-based for now, API-ready for later"""

    DEFAULT_CSV_PATH = "data/weather_baku_2026.csv"

    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or self.DEFAULT_CSV_PATH
        self.data: Optional[pd.DataFrame] = None
        self._load_csv()

    def _load_csv(self) -> None:
        """Load weather CSV into memory"""
        try:
            path = Path(self.csv_path)
            if not path.exists():
                logger.warning(f"⚠️ Weather CSV not found: {self.csv_path}")
                self.data = pd.DataFrame()
                return

            self.data = pd.read_csv(self.csv_path, parse_dates=['date'])
            self.data = self.data.sort_values('date').reset_index(drop=True)

            logger.info(
                f"✅ Weather CSV loaded: {len(self.data)} rows "
                f"({self.data['date'].min().date()} → {self.data['date'].max().date()})"
            )
        except Exception as e:
            logger.error(f"❌ Failed to load weather CSV: {e}")
            self.data = pd.DataFrame()

    # --------------------------------------------
    # 📖 PUBLIC API (same shape as future API version)
    # --------------------------------------------

    def get_weather_for_date(self, date: datetime) -> Optional[WeatherData]:
        """Get weather for a specific date"""
        if self.data.empty:
            return None

        date_only = pd.Timestamp(date).normalize()
        match = self.data[self.data['date'] == date_only]

        if match.empty:
            return self._get_mock_weather(date)

        row = match.iloc[0]
        return self._row_to_weather_data(row)

    def get_weather_range(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[WeatherData]:
        """Get weather for a date range"""
        if self.data.empty:
            return []

        start = pd.Timestamp(start_date).normalize()
        end = pd.Timestamp(end_date).normalize()

        mask = (self.data['date'] >= start) & (self.data['date'] <= end)
        subset = self.data[mask]

        return [self._row_to_weather_data(row) for _, row in subset.iterrows()]

    def get_forecast(self, days: int = 7) -> List[WeatherData]:
        """Get weather for the next N days (from CSV or mock)"""
        today = pd.Timestamp.now().normalize()
        end = today + pd.Timedelta(days=days)
        return self.get_weather_range(today, end)

    # --------------------------------------------
    # 🔧 INTERNAL HELPERS
    # --------------------------------------------

    def _row_to_weather_data(self, row: pd.Series) -> WeatherData:
        """Convert a CSV row to WeatherData"""
        temp = float(row['temperature'])
        return WeatherData(
            date=row['date'].to_pydatetime(),
            temperature=temp,
            feels_like=temp - 2.0,  # Simple approximation
            humidity=int(row['humidity']),
            pressure=1013,  # Not in CSV yet, default
            wind_speed=float(row['wind_speed']),
            condition=str(row['condition']).lower(),
            precipitation=float(row['precipitation']),
            is_extreme=self._is_extreme(row),
        )

    def _is_extreme(self, row: pd.Series) -> bool:
        """Check if weather is extreme"""
        condition = str(row['condition']).lower()
        extreme_conditions = ['storm', 'thunderstorm', 'hurricane', 'tornado', 'blizzard']

        if any(c in condition for c in extreme_conditions):
            return True
        if float(row['temperature']) > 40 or float(row['temperature']) < -10:
            return True
        if float(row['wind_speed']) > 25:
            return True

        return False

    def _get_mock_weather(self, dt: datetime) -> WeatherData:
        """Fallback mock weather if date not in CSV"""
        import numpy as np

        month = dt.month
        if month in [12, 1, 2]:
            base_temp = 5
        elif month in [3, 4, 5]:
            base_temp = 15
        elif month in [6, 7, 8]:
            base_temp = 25
        else:
            base_temp = 15

        return WeatherData(
            date=dt,
            temperature=base_temp,
            feels_like=base_temp - 2,
            humidity=65,
            pressure=1013,
            wind_speed=10.0,
            condition='clear',
            precipitation=0.0,
            is_extreme=False,
        )

    # --------------------------------------------
    # 📊 SALES IMPACT
    # --------------------------------------------

    def get_weather_impact_factor(self, weather: WeatherData) -> float:
        """Calculate sales impact multiplier based on weather"""
        factor = 1.0

        # Temperature impact
        if weather.temperature > 35:
            factor *= 0.75   # Extreme heat
        elif weather.temperature > 30:
            factor *= 0.85   # Very hot
        elif weather.temperature > 25:
            factor *= 1.10   # Nice weather
        elif weather.temperature < 0:
            factor *= 0.85   # Freezing
        elif weather.temperature < 5:
            factor *= 0.95   # Cold

        # Rain impact
        if weather.precipitation > 5:
            factor *= 0.70   # Heavy rain
        elif weather.precipitation > 1:
            factor *= 0.90   # Moderate rain
        elif weather.precipitation > 0:
            factor *= 0.97   # Light rain

        # Extreme events
        if weather.is_extreme:
            factor *= 0.50

        return round(factor, 3)


# ============================================
# 🎯 HIGH-LEVEL SERVICE
# ============================================

class WeatherService:
    """High-level weather service for predictions"""

    def __init__(self, csv_path: Optional[str] = None):
        self.connector = WeatherConnector(csv_path)

    def get_sales_multiplier(self, date: datetime) -> float:
        """Get weather-based sales multiplier for a date"""
        weather = self.connector.get_weather_for_date(date)
        if not weather:
            return 1.0
        return self.connector.get_weather_impact_factor(weather)

    def get_weather_features(self, date: datetime) -> Dict[str, float]:
        """Get weather as a feature dict for ML model"""
        weather = self.connector.get_weather_for_date(date)
        if not weather:
            return {
                'weather_temperature': 0.0,
                'weather_humidity': 0.0,
                'weather_precipitation': 0.0,
                'weather_wind_speed': 0.0,
                'weather_is_extreme': 0,
                'weather_impact_factor': 1.0,
            }

        return {
            'weather_temperature': weather.temperature,
            'weather_humidity': float(weather.humidity),
            'weather_precipitation': weather.precipitation,
            'weather_wind_speed': weather.wind_speed,
            'weather_is_extreme': int(weather.is_extreme),
            'weather_impact_factor': self.connector.get_weather_impact_factor(weather),
        }