"""Calendar API connector - fetches holidays and special events"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Calendar event structure"""
    date: datetime
    name: str
    type: str  # 'holiday', 'religious', 'seasonal', 'promotion'
    impact_factor: float
    days_lead: int  # How many days before event it affects sales
    days_lag: int   # How many days after event it affects sales


class CalendarConnector:
    """Connector for holiday and event calendar"""
    
    def __init__(self):
        self.events = self._load_events()
        self.cache = {}
    
    def _load_events(self) -> List[CalendarEvent]:
        """Load all known events"""
        
        events = []
        
        # Fixed date holidays
        fixed_holidays = [
            ('New Year', '2025-01-01', 'holiday', 0.8, 3, 1),
            ('Valentine Day', '2025-02-14', 'holiday', 1.6, 7, 1),
            ('International Women Day', '2025-03-08', 'holiday', 1.3, 3, 1),
            ('Black Friday', '2025-11-28', 'shopping', 2.5, 7, 1),
            ('Christmas', '2025-12-25', 'holiday', 1.4, 14, 3),
            ('New Year Eve', '2025-12-31', 'holiday', 1.3, 7, 2),
        ]
        
        for name, date_str, event_type, impact, lead, lag in fixed_holidays:
            events.append(CalendarEvent(
                date=datetime.strptime(date_str, '%Y-%m-%d'),
                name=name,
                type=event_type,
                impact_factor=impact,
                days_lead=lead,
                days_lag=lag
            ))
        
        # Religious events (dates vary by year)
        # Ramadan 2025
        events.append(CalendarEvent(
            date=datetime(2025, 3, 1),
            name='Ramadan Start',
            type='religious',
            impact_factor=1.4,
            days_lead=15,
            days_lag=30
        ))
        
        # Eid al-Fitr 2025
        events.append(CalendarEvent(
            date=datetime(2025, 3, 31),
            name='Eid al-Fitr',
            type='religious',
            impact_factor=2.0,
            days_lead=3,
            days_lag=3
        ))
        
        # Eid al-Adha 2025
        events.append(CalendarEvent(
            date=datetime(2025, 6, 7),
            name='Eid al-Adha',
            type='religious',
            impact_factor=1.8,
            days_lead=3,
            days_lag=3
        ))
        
        return events
    
    def get_events_for_date(self, date: datetime) -> List[CalendarEvent]:
        """Get all events affecting a specific date"""
        
        date_key = date.date()
        
        if date_key in self.cache:
            return self.cache[date_key]
        
        affecting_events = []
        
        for event in self.events:
            # Check if date is within event's influence window
            start = event.date - timedelta(days=event.days_lead)
            end = event.date + timedelta(days=event.days_lag)
            
            if start <= date <= end:
                affecting_events.append(event)
        
        self.cache[date_key] = affecting_events
        return affecting_events
    
    def get_sales_multiplier(self, date: datetime) -> float:
        """Calculate sales multiplier based on calendar events"""
        
        events = self.get_events_for_date(date)
        
        if not events:
            return 1.0
        
        # Combine multipliers from all events affecting this date
        multiplier = 1.0
        for event in events:
            # Calculate distance from event
            days_diff = (event.date - date).days
            
            # Reduce impact as we move away from event
            if days_diff > 0:  # Before event
                distance_factor = 1 - (days_diff / event.days_lead) * 0.5
            else:  # After event
                distance_factor = 1 - (abs(days_diff) / event.days_lag) * 0.5
            
            multiplier *= 1 + (event.impact_factor - 1) * max(0, distance_factor)
        
        return multiplier
    
    def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming events for planning"""
        
        today = datetime.now()
        upcoming = []
        
        for event in self.events:
            if event.date >= today:
                days_until = (event.date - today).days
                if days_until <= days_ahead:
                    upcoming.append({
                        'name': event.name,
                        'date': event.date.strftime('%Y-%m-%d'),
                        'type': event.type,
                        'days_until': days_until,
                        'expected_impact': event.impact_factor,
                        'preparation_needed': days_until <= event.days_lead
                    })
        
        return sorted(upcoming, key=lambda x: x['days_until'])
    
    def get_seasonal_factor(self, date: datetime) -> float:
        """Get seasonal sales factor"""
        
        month = date.month
        
        # Seasonal patterns based on month
        seasonal = {
            1: 0.9,   # January - post-holiday slowdown
            2: 0.95,  # February - normal
            3: 1.1,   # March - Ramadan effect
            4: 1.15,  # April - Eid effect
            5: 1.0,   # May - normal
            6: 0.95,  # June - normal
            7: 0.9,   # July - summer slowdown
            8: 0.95,  # August - back to school prep
            9: 1.1,   # September - back to school
            10: 1.0,  # October - normal
            11: 1.3,  # November - Black Friday
            12: 1.5,  # December - Christmas
        }
        
        return seasonal.get(month, 1.0)


class CalendarService:
    """High-level calendar service for predictions"""
    
    def __init__(self):
        self.connector = CalendarConnector()
    
    def get_sales_multiplier(self, date: datetime) -> float:
        """Get combined calendar-based sales multiplier"""
        
        event_multiplier = self.connector.get_sales_multiplier(date)
        seasonal_multiplier = self.connector.get_seasonal_factor(date)
        
        return event_multiplier * seasonal_multiplier
    
    def get_event_impact(self, date: datetime) -> Dict:
        """Get detailed event impact analysis"""
        
        events = self.connector.get_events_for_date(date)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'total_multiplier': self.get_sales_multiplier(date),
            'events': [
                {
                    'name': e.name,
                    'type': e.type,
                    'impact': e.impact_factor,
                    'days_to_event': (e.date - date).days
                }
                for e in events
            ],
            'seasonal_multiplier': self.connector.get_seasonal_factor(date)
        }