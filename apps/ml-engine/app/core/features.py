import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

class FeatureEngineer:
    """Advanced feature engineering for time-series forecasting"""
    
    def __init__(self):
        self.feature_columns = []
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create all features"""
        df = df.copy()
        
        # Time features
        df = self._add_time_features(df)
        
        # Lag features
        df = self._add_lag_features(df)
        
        # Rolling statistics
        df = self._add_rolling_features(df)
        
        # Holiday features
        df = self._add_holiday_features(df)
        
        # Advanced features
        df = self._add_advanced_features(df)
        
        # Clean up
        df = self._clean_features(df)
        
        self.feature_columns = [c for c in df.columns if c != 'sales']
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add temporal features"""
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['day_of_year'] = df['date'].dt.dayofyear
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        # Cyclical encoding
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lag features"""
        lags = [1, 2, 3, 7, 14, 28]  # Daily, weekly, monthly
        for lag in lags:
            df[f'lag_{lag}'] = df['sales'].shift(lag)
            
        # Seasonal lags (same day last week, last month)
        df['lag_7'] = df['sales'].shift(7)
        df['lag_28'] = df['sales'].shift(28)
        
        return df
    
    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rolling statistics"""
        windows = [3, 7, 14, 30]
        
        for window in windows:
            df[f'rolling_mean_{window}'] = df['sales'].rolling(window).mean()
            df[f'rolling_std_{window}'] = df['sales'].rolling(window).std()
            df[f'rolling_min_{window}'] = df['sales'].rolling(window).min()
            df[f'rolling_max_{window}'] = df['sales'].rolling(window).max()
        
        # Rolling trends
        df['rolling_trend_7'] = df['rolling_mean_7'] - df['rolling_mean_14']
        df['rolling_trend_30'] = df['rolling_mean_30'] - df['rolling_mean_14']
        
        return df
    
    def _add_holiday_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add holiday indicators"""
        # Use existing is_holiday column if present
        if 'is_holiday' in df.columns:
            df['is_holiday'] = df['is_holiday'].astype(int)
        else:
            df['is_holiday'] = 0
        
        # Holiday lead/lag
        for days in [3, 7, 14]:
            df[f'holiday_lead_{days}'] = df['is_holiday'].shift(-days).fillna(0)
            df[f'holiday_lag_{days}'] = df['is_holiday'].shift(days).fillna(0)
        
        return df
    
    def _add_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced features"""
        # Price elasticity proxy
        if 'price' in df.columns:
            df['price_change'] = df['price'].pct_change()
            df['price_sales_interaction'] = df['price'] * df['sales']
        
        # Moving average ratio (shows relative performance)
        df['ma_ratio_7'] = df['sales'] / df['rolling_mean_7'].clip(lower=1)
        df['ma_ratio_30'] = df['sales'] / df['rolling_mean_30'].clip(lower=1)
        
        # Day-over-day change
        df['daily_change'] = df['sales'].pct_change()
        df['daily_change_abs'] = df['sales'].diff()
        
        # Running total
        df['running_sum_30'] = df['sales'].rolling(30).sum()
        
        return df
    
    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean up NaN and infinite values"""
        # Replace infinity
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Forward fill then backward fill
        df = df.bfill().ffill()
        
        # Fill remaining NaNs with 0
        df = df.fillna(0)
        
        return df