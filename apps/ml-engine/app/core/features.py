import pandas as pd
import numpy as np
from .holiday_bank import HolidayBank
from .season_bank import SeasonBank

class FeatureEngineer:
    """Advanced feature engineering for time-series forecasting""" 
    def __init__(self, holidays_csv_path: str = "data/holidays.csv", seasons_csv_path: str = "data/seasons.csv"):
        self.feature_columns = []
        self.holiday_bank = HolidayBank(holidays_csv_path)
        self.season_bank = SeasonBank(seasons_csv_path)

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create all features"""
        df = df.copy()
        
        # Time features
        df = self._add_time_features(df)
        
        # Lag features
        df = self._add_lag_features(df)
        
        # Rolling statistics
        df = self._add_rolling_features(df)

        # Seasonal effects
        df = self._add_season_features(df)
        
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
        # Basic features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['day_of_year'] = df['date'].dt.dayofyear
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    
        # 🆕 More cyclical encoding
        # Day of week: 0-6 → sine/cosine
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
        # Month: 1-12 → sine/cosine
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
        # 🆕 Day of month: 1-31 → sine/cosine
        df['day_of_month_sin'] = np.sin(2 * np.pi * df['day_of_month'] / 31)
        df['day_of_month_cos'] = np.cos(2 * np.pi * df['day_of_month'] / 31)
    
        # 🆕 Quarter: 1-4 → sine/cosine
        df['quarter_sin'] = np.sin(2 * np.pi * df['quarter'] / 4)
        df['quarter_cos'] = np.cos(2 * np.pi * df['quarter'] / 4)
    
        # 🆕 Week of year: 1-52 → sine/cosine
        df['week_of_year_sin'] = np.sin(2 * np.pi * df['week_of_year'] / 52)
        df['week_of_year_cos'] = np.cos(2 * np.pi * df['week_of_year'] / 52)
    
        # 🆕 Day of year: 1-365 → sine/cosine
        df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
        df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
    
        return df    

    def _add_holiday_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add holiday features using the flexible holiday bank"""
        
        # Initialize holiday columns
        df['is_holiday'] = 0
        df['holiday_name'] = ''
        df['holiday_impact_strength'] = 0
        df['pre_impact_days'] = 0
        df['post_impact_days'] = 0
        df['days_to_holiday'] = 999
        df['days_since_holiday'] = 999
        df['holiday_intensity'] = 0
        
        # Get category from dataframe (if available)
        category = df.get('category', 'All')
        if isinstance(category, pd.Series):
            category = category.iloc[0] if len(category) > 0 else 'All'
        
        # Apply holiday impact for each row
        for idx, row in df.iterrows():
            date = row['date']
            impact = self.holiday_bank.get_holiday_impact(date, category)
            
            df.loc[idx, 'is_holiday'] = int(impact['is_holiday'])
            df.loc[idx, 'holiday_name'] = impact['holiday_name'] or ''
            df.loc[idx, 'holiday_impact_strength'] = impact['impact_strength']
            df.loc[idx, 'pre_impact_days'] = impact['pre_impact']
            df.loc[idx, 'post_impact_days'] = impact['post_impact']
            df.loc[idx, 'days_to_holiday'] = impact['days_until_holiday']
            df.loc[idx, 'days_since_holiday'] = impact['days_since_holiday']
            df.loc[idx, 'holiday_intensity'] = impact['impact_strength']
        
        # 🆕 Aggregate holiday features
        # Rolling holiday impact
        df['holiday_intensity_7'] = df['holiday_intensity'].rolling(7, min_periods=1).mean()
        df['holiday_intensity_14'] = df['holiday_intensity'].rolling(14, min_periods=1).mean()
        df['holiday_intensity_30'] = df['holiday_intensity'].rolling(30, min_periods=1).mean()
        
        # Days since/until nearest holiday
        df['days_to_holiday_clamped'] = df['days_to_holiday'].clip(upper=30)
        df['days_since_holiday_clamped'] = df['days_since_holiday'].clip(upper=30)
        
        # Holiday week indicators
        df['holiday_week_before'] = ((df['days_to_holiday'] <= 7) & (df['days_to_holiday'] > 0)).astype(int)
        df['holiday_week_after'] = ((df['days_since_holiday'] <= 7) & (df['days_since_holiday'] > 0)).astype(int)
        
        return df

    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lag features for daily, weekly, monthly, and quarterly patterns"""
    
        # Define lags
        lags = [
            1,    # Yesterday
            2,    # 2 days ago
            3,    # 3 days ago
            7,    # Same day last week (weekly seasonality)
            14,   # Same day 2 weeks ago
            21,   # Same day 3 weeks ago 🆕
            28,   # Same day 4 weeks ago (monthly seasonality)
            30,   # 30 days ago 🆕
            60,   # 60 days ago (bi-monthly) 🆕
            90,   # 90 days ago (quarterly) 🆕
        ]
    
        # Create all lag features
        for lag in lags:
            df[f'lag_{lag}'] = df['sales'].shift(lag)
    
        # Optional: Add lag differences (change from previous periods)
        df['lag_diff_1'] = df['lag_1'] - df['lag_2']  # Day-over-day change
        df['lag_diff_7'] = df['lag_7'] - df['lag_14'] # Week-over-week change
        df['lag_diff_28'] = df['lag_28'] - df['lag_30'] # Month-over-month change
    
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
        
    def _add_season_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add season features using the flexible season bank"""
        
        # Initialize season columns
        df['season_name'] = ''
        df['is_season'] = 0
        df['season_impact_strength'] = 0
        df['season_impact_category'] = ''
        df['season_region'] = ''
        df['days_until_season_ends'] = 0
        df['days_in_season'] = 0
        df['season_transition_type'] = ''
        df['season_transition_impact'] = 0
        
        # Get category from dataframe
        category = df.get('category', 'All')
        if isinstance(category, pd.Series):
            category = category.iloc[0] if len(category) > 0 else 'All'
        
        # Apply season impact for each row
        for idx, row in df.iterrows():
            date = row['date']
            
            # Main season impact
            impact = self.season_bank.get_season_impact(date, category)
            df.loc[idx, 'season_name'] = impact['season_name'] or ''
            df.loc[idx, 'is_season'] = int(impact['is_season'])
            df.loc[idx, 'season_impact_strength'] = impact['impact_strength']
            df.loc[idx, 'season_impact_category'] = impact['impact_category'] or ''
            df.loc[idx, 'season_region'] = impact['region'] or ''
            df.loc[idx, 'days_until_season_ends'] = impact['days_until_season_ends']
            df.loc[idx, 'days_in_season'] = impact['days_in_season']
            
            # Season transition
            transition = self.season_bank.get_season_transition(date, category)
            df.loc[idx, 'season_transition_type'] = transition['transition_type'] or ''
            df.loc[idx, 'season_transition_impact'] = transition['transition_impact']
        
        # 🆕 Aggregate season features
        df['season_impact_7'] = df['season_impact_strength'].rolling(7, min_periods=1).mean()
        df['season_impact_14'] = df['season_impact_strength'].rolling(14, min_periods=1).mean()
        df['season_impact_30'] = df['season_impact_strength'].rolling(30, min_periods=1).mean()
        
        # 🆕 Season intensity (peak season effect)
        df['season_intensity'] = df['season_impact_strength'] * df['is_season']
        df['season_intensity_7'] = df['season_intensity'].rolling(7, min_periods=1).mean()
        
        # 🆕 Season transition indicators
        df['is_season_start'] = (df['season_transition_type'] == 'pre_season').astype(int)
        df['is_season_end'] = (df['season_transition_type'] == 'post_season').astype(int)
        
        # 🆕 Multiple season overlap detection
        # (For regions with multiple seasons like monsoon + summer)
        
        return df
    
    def _add_combined_holiday_season_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add combined holiday + season features"""
        
        # Holiday-Season interaction
        df['holiday_season_interaction'] = df['holiday_intensity'] * df['season_intensity']
        df['holiday_season_avg'] = (df['holiday_intensity'] + df['season_intensity']) / 2
        
        # Combined impact score
        df['combined_impact'] = (
            df['holiday_intensity'] * 0.6 + 
            df['season_intensity'] * 0.4
        )
        
        # Event type classification
        df['event_type'] = 'normal'
        df.loc[df['is_holiday'] == 1, 'event_type'] = 'holiday'
        df.loc[df['is_season'] == 1, 'event_type'] = 'season'
        df.loc[(df['is_holiday'] == 1) & (df['is_season'] == 1), 'event_type'] = 'holiday+season'
        
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