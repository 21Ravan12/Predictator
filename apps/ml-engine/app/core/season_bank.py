import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class SeasonBank:
    """Flexible season bank with configurable impact periods"""
    
    def __init__(self, seasons_csv_path: str = "data/seasons.csv"):
        self.seasons_df = pd.read_csv(seasons_csv_path, parse_dates=['start_date', 'end_date'])
        self.seasons_list = self._create_seasons_list()
        
    def _create_seasons_list(self) -> List[Dict]:
        """Convert CSV to list of season dictionaries"""
        seasons = []
        for _, row in self.seasons_df.iterrows():
            seasons.append({
                'name': row['season_name'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'region': row['region'],
                'impact_category': row['impact_category'],
                'impact_strength': row['impact_strength'],
                'pre_impact_days': row['pre_impact_days'],
                'post_impact_days': row['post_impact_days'],
                'description': row.get('description', ''),
                'affected_categories': row['affected_categories'].split(',') if isinstance(row['affected_categories'], str) else ['All']
            })
        return seasons
    
    def get_season_impact(self, date: pd.Timestamp, category: str = 'All') -> Dict:
        """Get season impact for a specific date and category"""
        
        # Check if date is in any season
        for season in self.seasons_list:
            if season['start_date'] <= date <= season['end_date']:
                if 'All' in season['affected_categories'] or category in season['affected_categories']:
                    return {
                        'season_name': season['name'],
                        'is_season': True,
                        'impact_strength': season['impact_strength'],
                        'impact_category': season['impact_category'],
                        'region': season['region'],
                        'days_until_season_ends': (season['end_date'] - date).days,
                        'days_in_season': (date - season['start_date']).days,
                    }
        
        # No season impact
        return {
            'season_name': None,
            'is_season': False,
            'impact_strength': 0,
            'impact_category': None,
            'region': None,
            'days_until_season_ends': 0,
            'days_in_season': 0,
        }
    
    def get_season_transition(self, date: pd.Timestamp, category: str = 'All') -> Dict:
        """Get season transition effects (entering/leaving a season)"""
        
        # Check pre-impact (days before season starts)
        for season in self.seasons_list:
            pre_days = season['pre_impact_days']
            for day_offset in range(1, pre_days + 1):
                check_date = season['start_date'] - timedelta(days=day_offset)
                if check_date.date() == date.date():
                    if 'All' in season['affected_categories'] or category in season['affected_categories']:
                        return {
                            'season_name': season['name'],
                            'transition_type': 'pre_season',
                            'days_until_season': day_offset,
                            'transition_impact': season['impact_strength'] * (1 - (day_offset / pre_days)),
                            'region': season['region']
                        }
            
            # Check post-impact (days after season ends)
            post_days = season['post_impact_days']
            for day_offset in range(1, post_days + 1):
                check_date = season['end_date'] + timedelta(days=day_offset)
                if check_date.date() == date.date():
                    if 'All' in season['affected_categories'] or category in season['affected_categories']:
                        return {
                            'season_name': season['name'],
                            'transition_type': 'post_season',
                            'days_since_season_ended': day_offset,
                            'transition_impact': season['impact_strength'] * (1 - (day_offset / post_days)),
                            'region': season['region']
                        }
        
        return {
            'season_name': None,
            'transition_type': None,
            'transition_impact': 0,
            'region': None
        }
    
    def add_season(self,
                   name: str,
                   start_date: str,
                   end_date: str,
                   region: str = 'Northern',
                   impact_category: str = 'Weather',
                   impact_strength: int = 5,
                   pre_impact_days: int = 3,
                   post_impact_days: int = 3,
                   affected_categories: List[str] = ['All'],
                   description: str = ''):
        """Add a new season programmatically"""
        new_row = {
            'season_name': name,
            'start_date': pd.to_datetime(start_date),
            'end_date': pd.to_datetime(end_date),
            'region': region,
            'impact_category': impact_category,
            'impact_strength': impact_strength,
            'pre_impact_days': pre_impact_days,
            'post_impact_days': post_impact_days,
            'description': description,
            'affected_categories': ','.join(affected_categories)
        }
        self.seasons_df = pd.concat([self.seasons_df, pd.DataFrame([new_row])], ignore_index=True)
        self.seasons_list = self._create_seasons_list()
        
        # Save to CSV
        self.seasons_df.to_csv('data/seasons.csv', index=False)
        print(f"✅ Added season: {name} from {start_date} to {end_date}")
        