"""Data validation utilities"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import re


def validate_date(date: Any) -> Tuple[bool, Optional[str]]:
    """Validate date format"""
    try:
        if isinstance(date, str):
            pd.to_datetime(date)
        elif isinstance(date, datetime):
            pass
        else:
            return False, "Date must be string or datetime"
        return True, None
    except Exception as e:
        return False, f"Invalid date: {str(e)}"


def validate_sales_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate sales data DataFrame"""
    errors = []
    
    # Check required columns
    required = ['date', 'sales']
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
    
    # Check date column
    if 'date' in df.columns:
        try:
            pd.to_datetime(df['date'])
        except:
            errors.append("Invalid date format")
    
    # Check sales column
    if 'sales' in df.columns:
        if df['sales'].dtype not in ['int64', 'float64']:
            errors.append("Sales must be numeric")
        
        if (df['sales'] < 0).any():
            errors.append("Sales cannot be negative")
        
        if df['sales'].isna().sum() > len(df) * 0.3:
            errors.append("Too many missing sales values")
    
    # Check data sufficiency
    if len(df) < 30:
        errors.append(f"Need at least 30 records, got {len(df)}")
    
    return len(errors) == 0, errors


def validate_product_id(product_id: Any) -> Tuple[bool, Optional[str]]:
    """Validate product ID format"""
    if not product_id:
        return False, "Product ID cannot be empty"
    
    if not isinstance(product_id, str):
        return False, "Product ID must be string"
    
    if len(product_id) > 100:
        return False, "Product ID too long (max 100 chars)"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', product_id):
        return False, "Product ID contains invalid characters"
    
    return True, None


def validate_prediction_request(data: Dict) -> Tuple[bool, List[str]]:
    """Validate prediction request data"""
    errors = []
    
    # Check product_id
    product_id = data.get('product_id')
    if not product_id:
        errors.append("product_id is required")
    else:
        valid, error = validate_product_id(product_id)
        if not valid:
            errors.append(error)
    
    # Check days_ahead
    days_ahead = data.get('days_ahead', 7)
    if not isinstance(days_ahead, int):
        errors.append("days_ahead must be integer")
    elif days_ahead < 1 or days_ahead > 30:
        errors.append("days_ahead must be between 1 and 30")
    
    # Check floor_limit
    floor_limit = data.get('floor_limit', 0)
    if not isinstance(floor_limit, (int, float)):
        errors.append("floor_limit must be number")
    elif floor_limit < 0:
        errors.append("floor_limit cannot be negative")
    
    return len(errors) == 0, errors


def validate_training_request(data: Dict) -> Tuple[bool, List[str]]:
    """Validate training request data"""
    errors = []
    
    csv_path = data.get('csv_path')
    if csv_path and not isinstance(csv_path, str):
        errors.append("csv_path must be string")
    
    force_retrain = data.get('force_retrain', False)
    if not isinstance(force_retrain, bool):
        errors.append("force_retrain must be boolean")
    
    return len(errors) == 0, errors


def validate_threshold(value: float, min_val: float = 0, max_val: float = 100) -> bool:
    """Validate numeric threshold"""
    return min_val <= value <= max_val


def validate_percentage(percentage: float) -> bool:
    """Validate percentage value (0-100)"""
    return 0 <= percentage <= 100


def validate_positive_number(value: Any) -> Tuple[bool, Optional[str]]:
    """Validate positive number"""
    try:
        num = float(value)
        if num < 0:
            return False, "Value must be positive"
        return True, None
    except (ValueError, TypeError):
        return False, "Value must be a number"


def validate_json_schema(data: Dict, required_fields: List[str]) -> Tuple[bool, List[str]]:
    """Validate JSON against required fields"""
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, [f"Missing fields: {missing}"]
    return True, []


def sanitize_input(text: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    
    # Remove special characters
    text = re.sub(r'[^\w\s\-_]', '', text)
    # Trim length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()