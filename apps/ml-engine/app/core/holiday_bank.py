from datetime import timedelta
from typing import Dict, List

import pandas as pd
from pandas import Timestamp


class HolidayBank:
    """Flexible holiday bank with configurable impact periods"""
    
    def __init__(self, holidays_csv_path: str = "data/holidays.csv"):
        self.holidays_df = pd.read_csv(holidays_csv_path, parse_dates=['date'])
        self.holidays_dict = self._create_holiday_dict()
        
    def _create_holiday_dict(self) -> Dict:
        """Convert CSV to dictionary for faster lookup"""
        holidays = {}
        for _, row in self.holidays_df.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            holidays[date_str] = {
                'name': row['holiday_name'],
                'date': row['date'],
                'pre_impact_days': row['pre_impact_days'],
                'post_impact_days': row['post_impact_days'],
                'impact_strength': row['impact_strength'],
                'affected_categories': str(row['affected_categories']).split(','),
                'description': row.get('description', '')
            }
        return holidays
    
    def get_holiday_impact(self, date: pd.Timestamp, category: str = 'All') -> Dict:
        """Get holiday impact for a specific date and category"""
        date_str = date.strftime('%Y-%m-%d')
        
        # Check if this date is a holiday
        if date_str in self.holidays_dict:
            holiday = self.holidays_dict[date_str]
            if 'All' in holiday['affected_categories'] or category in holiday['affected_categories']:
                return {
                    'is_holiday': True,
                    'holiday_name': holiday['name'],
                    'impact_strength': holiday['impact_strength'],
                    'pre_impact': 0,
                    'post_impact': 0,
                    'days_until_holiday': 0,
                    'days_since_holiday': 0
                }
        
        # Check if this date is in pre-impact period
        for holiday_date_str, holiday in self.holidays_dict.items():
            holiday_date = holiday['date']
            
            # Pre-impact period
            pre_days = holiday['pre_impact_days']
            for day_offset in range(1, pre_days + 1):
                check_date = holiday_date - timedelta(days=day_offset)
                if check_date.strftime('%Y-%m-%d') == date_str:
                    if 'All' in holiday['affected_categories'] or category in holiday['affected_categories']:
                        return {
                            'is_holiday': False,
                            'holiday_name': holiday['name'],
                            'impact_strength': holiday['impact_strength'] * (1 - (day_offset / pre_days)),
                            'pre_impact': day_offset,
                            'post_impact': 0,
                            'days_until_holiday': day_offset,
                            'days_since_holiday': 0
                        }
            
            # Post-impact period
            post_days = holiday['post_impact_days']
            for day_offset in range(1, post_days + 1):
                check_date = holiday_date + timedelta(days=day_offset)
                if check_date.strftime('%Y-%m-%d') == date_str:
                    if 'All' in holiday['affected_categories'] or category in holiday['affected_categories']:
                        return {
                            'is_holiday': False,
                            'holiday_name': holiday['name'],
                            'impact_strength': holiday['impact_strength'] * (1 - (day_offset / post_days)),
                            'pre_impact': 0,
                            'post_impact': day_offset,
                            'days_until_holiday': 0,
                            'days_since_holiday': day_offset
                        }
        
        # No holiday impact
        return {
            'is_holiday': False,
            'holiday_name': None,
            'impact_strength': 0,
            'pre_impact': 0,
            'post_impact': 0,
            'days_until_holiday': 999,
            'days_since_holiday': 999
        }
    
    def add_holiday(self, 
                    name: str, 
                    date: str, 
                    pre_impact_days: int = 3,
                    post_impact_days: int = 2,
                    impact_strength: int = 5,
                    affected_categories: List[str] = ['All'],
                    description: str = ''):
        """Add a new holiday programmatically"""
        new_row = {
            'holiday_name': name,
            'date': pd.to_datetime(date),
            'pre_impact_days': pre_impact_days,
            'post_impact_days': post_impact_days,
            'impact_strength': impact_strength,
            'affected_categories': ','.join(affected_categories),
            'description': description
        }
        self.holidays_df = pd.concat([self.holidays_df, pd.DataFrame([new_row])], ignore_index=True)
        self.holidays_dict = self._create_holiday_dict()
        
        # Save to CSV
        self.holidays_df.to_csv('data/holidays.csv', index=False)
        print(f"✅ Added holiday: {name} on {date}")

