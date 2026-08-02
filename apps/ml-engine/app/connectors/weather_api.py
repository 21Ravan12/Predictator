"""Weather API connector - fetches real-time and forecast weather data"""

try:
    import aiohttp
except ImportError:
    aiohttp = None
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Weather data structure"""
    date: datetime
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    condition: str
    precipitation: float
    is_extreme: bool


class WeatherConnector:
    """Connector for OpenWeatherMap API"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENWEATHER_API_KEY
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def _get_cache_key(self, location: str, date: str) -> str:
        """Generate cache key"""
        return f"{location}:{date}"
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cache entry is still valid"""
        return datetime.now() - timestamp < self.cache_duration
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Get current weather for coordinates"""
        
        cache_key = self._get_cache_key(f"{lat},{lon}", "current")
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                logger.debug(f"Returning cached weather for {lat},{lon}")
                return cached_data
        
        if not self.api_key:
            logger.warning("No API key provided, returning mock data")
            return self._get_mock_weather(datetime.now())
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/weather"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric'  # Celsius
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather = self._parse_weather_data(data, datetime.now())
                        
                        # Cache the result
                        self.cache[cache_key] = (weather, datetime.now())
                        
                        return weather
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_mock_weather(datetime.now())
                        
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
            return self._get_mock_weather(datetime.now())
    
    async def get_forecast(self, lat: float, lon: float, days: int = 7) -> List[WeatherData]:
        """Get weather forecast for multiple days"""
        
        if not self.api_key:
            logger.warning("No API key provided, returning mock forecast")
            return [self._get_mock_weather(datetime.now() + timedelta(days=i)) for i in range(days)]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/forecast"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric',
                    'cnt': days * 8  # 3-hour intervals
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_forecast_data(data, days)
                    else:
                        logger.error(f"Forecast API error: {response.status}")
                        return [self._get_mock_weather(datetime.now() + timedelta(days=i)) for i in range(days)]
                        
        except Exception as e:
            logger.error(f"Failed to fetch forecast: {e}")
            return [self._get_mock_weather(datetime.now() + timedelta(days=i)) for i in range(days)]
    
    def _parse_weather_data(self, data: Dict, dt: datetime) -> WeatherData:
        """Parse API response to WeatherData object"""
        return WeatherData(
            date=dt,
            temperature=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            wind_speed=data['wind']['speed'],
            condition=data['weather'][0]['description'],
            precipitation=data.get('rain', {}).get('1h', 0),
            is_extreme=self._is_extreme_weather(data)
        )
    
    def _parse_forecast_data(self, data: Dict, days: int) -> List[WeatherData]:
        """Parse forecast API response"""
        
        forecasts = []
        daily_data = {}
        
        for item in data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            date_key = dt.date()
            
            # Take daily average
            if date_key not in daily_data:
                daily_data[date_key] = []
            
            daily_data[date_key].append(item)
        
        for date_key, items in list(daily_data.items())[:days]:
            avg_temp = sum(i['main']['temp'] for i in items) / len(items)
            avg_humidity = sum(i['main']['humidity'] for i in items) / len(items)
            conditions = [i['weather'][0]['description'] for i in items]
            
            forecasts.append(WeatherData(
                date=datetime.combine(date_key, datetime.min.time()),
                temperature=avg_temp,
                feels_like=avg_temp,
                humidity=int(avg_humidity),
                pressure=items[0]['main']['pressure'],
                wind_speed=items[0]['wind']['speed'],
                condition=max(set(conditions), key=conditions.count),
                precipitation=sum(i.get('rain', {}).get('3h', 0) for i in items),
                is_extreme=False
            ))
        
        return forecasts
    
    def _is_extreme_weather(self, data: Dict) -> bool:
        """Check if weather is extreme"""
        conditions = [c['main'].lower() for c in data['weather']]
        extreme = ['storm', 'thunderstorm', 'hurricane', 'tornado', 'blizzard']
        return any(c in ' '.join(conditions) for c in extreme)
    
    def _get_mock_weather(self, dt: datetime) -> WeatherData:
        """Generate mock weather data for testing"""
        import numpy as np
        
        # Seasonal temperature
        month = dt.month
        if month in [12, 1, 2]:
            base_temp = 5  # Winter
        elif month in [3, 4, 5]:
            base_temp = 15  # Spring
        elif month in [6, 7, 8]:
            base_temp = 25  # Summer
        else:
            base_temp = 15  # Fall
        
        # Daily variation
        hour_effect = np.sin(dt.hour * 2 * np.pi / 24) * 5
        
        return WeatherData(
            date=dt,
            temperature=base_temp + hour_effect,
            feels_like=base_temp + hour_effect - 2,
            humidity=np.random.randint(40, 80),
            pressure=np.random.randint(1000, 1025),
            wind_speed=np.random.uniform(0, 15),
            condition=['clear', 'clouds', 'rain'][np.random.randint(0, 3)],
            precipitation=np.random.uniform(0, 5) if np.random.random() < 0.3 else 0,
            is_extreme=np.random.random() < 0.05
        )
    
    def get_weather_impact_factor(self, weather: WeatherData) -> float:
        """Calculate sales impact factor based on weather"""
        
        factor = 1.0
        
        # Temperature impact
        if weather.temperature > 30:
            factor *= 0.8  # Too hot - less shopping
        elif weather.temperature > 25:
            factor *= 1.1  # Nice weather - more shopping
        elif weather.temperature < 5:
            factor *= 0.9  # Too cold - less shopping
        
        # Rain impact
        if weather.precipitation > 5:
            factor *= 0.7  # Heavy rain - much less shopping
        elif weather.precipitation > 0:
            factor *= 0.9  # Light rain - slightly less
        
        # Extreme weather
        if weather.is_extreme:
            factor *= 0.5  # Extreme - huge impact
        
        return factor


class WeatherService:
    """High-level weather service for predictions"""
    
    def __init__(self):
        self.connector = WeatherConnector()
    
    async def get_sales_multiplier(self, lat: float, lon: float, date: datetime) -> float:
        """Get weather-based sales multiplier for a specific date"""
        
        # Check if date is today
        if date.date() == datetime.now().date():
            weather = await self.connector.get_current_weather(lat, lon)
        else:
            # For future dates, use forecast (simplified)
            forecast = await self.connector.get_forecast(lat, lon, 7)
            days_diff = (date - datetime.now()).days
            if 0 <= days_diff < len(forecast):
                weather = forecast[days_diff]
            else:
                return 1.0
        
        return self.connector.get_weather_impact_factor(weather) if weather else 1.0