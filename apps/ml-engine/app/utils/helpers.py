"""Helper utility functions"""

from datetime import datetime, timedelta
from typing import List, Any, Optional
import uuid
import random


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime to string"""
    return date.strftime(format_str)


def calculate_percentage(part: float, total: float, decimals: int = 2) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, decimals)


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safe division to avoid ZeroDivisionError"""
    return a / b if b != 0 else default


def round_sales(value: float, decimals: int = 0) -> int:
    """Round sales to nearest integer"""
    return int(round(value, decimals))


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate unique ID"""
    unique = str(uuid.uuid4())[:length]
    return f"{prefix}_{unique}" if prefix else unique


def chunks(lst: List[Any], size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def get_date_range(days: int) -> tuple:
    """Get start and end dates for a range"""
    end = datetime.now()
    start = end - timedelta(days=days)
    return start, end


def moving_average(data: List[float], window: int) -> List[float]:
    """Calculate moving average"""
    if len(data) < window:
        return data
    
    result = []
    for i in range(len(data) - window + 1):
        avg = sum(data[i:i+window]) / window
        result.append(avg)
    return result


def detect_outliers(data: List[float], multiplier: float = 1.5) -> List[int]:
    """Detect outlier indices using IQR method"""
    if len(data) < 4:
        return []
    
    q1 = sorted(data)[len(data) // 4]
    q3 = sorted(data)[3 * len(data) // 4]
    iqr = q3 - q1
    
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    return [i for i, val in enumerate(data) if val < lower_bound or val > upper_bound]


def smooth_series(data: List[float], window: int = 3) -> List[float]:
    """Smooth time series with moving average"""
    result = []
    for i in range(len(data)):
        start = max(0, i - window // 2)
        end = min(len(data), i + window // 2 + 1)
        result.append(sum(data[start:end]) / (end - start))
    return result


def generate_trend_line(data: List[float]) -> tuple:
    """Generate linear trend line (slope, intercept)"""
    if len(data) < 2:
        return 0, 0
    
    x = list(range(len(data)))
    n = len(x)
    
    sum_x = sum(x)
    sum_y = sum(data)
    sum_xy = sum(x[i] * data[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
    
    return slope, intercept


def random_sales(base: float = 100, variation: float = 0.2) -> float:
    """Generate random sales around base value"""
    factor = 1 + random.uniform(-variation, variation)
    return max(0, base * factor)


def merge_dicts(dict1: dict, dict2: dict, overwrite: bool = True) -> dict:
    """Merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if overwrite or key not in result:
            result[key] = value
    return result


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix