import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class DictatorRule:
    name: str
    priority: int
    condition: callable
    action: callable
    alert_level: str  # 'info', 'warning', 'critical'

class DictatorEngine:
    """The Dictator - Enforces operational rules with an iron fist! 🤖"""
    
    def __init__(self):
        self.rules = self._load_rules()
        self.action_history = []
        
    def _load_rules(self):
        """Load all dictator rules"""
        return [
            DictatorRule(
                name="floor_limit_enforcement",
                priority=1,
                condition=lambda p, f: p['predicted'] < f['floor_limit'],
                action=self._enforce_floor_limit,
                alert_level="warning"
            ),
            DictatorRule(
                name="safety_stock_check",
                priority=2,
                condition=lambda p, f: p['current_stock'] < f['safety_stock'],
                action=self._recommend_reorder,
                alert_level="critical"
            ),
            DictatorRule(
                name="overstock_prevention",
                priority=3,
                condition=lambda p, f: p['predicted'] * 1.5 < p['current_stock'],
                action=self._suggest_discount,
                alert_level="info"
            ),
            DictatorRule(
                name="ramadan_uplift",
                priority=4,
                condition=lambda p, f: f['is_ramadan'],
                action=self._apply_ramadan_boost,
                alert_level="info"
            ),
        ]
    
    def _enforce_floor_limit(self, prediction: float, context: dict) -> Tuple[float, str]:
        """Force minimum stock level"""
        floor = context.get('floor_limit', 100)
        if prediction < floor:
            return floor, f"⚠️ DICTATOR: Increased from {prediction:.0f} to {floor} units"
        return prediction, None
    
    def _recommend_reorder(self, prediction: float, context: dict) -> Tuple[float, str]:
        """Recommend reorder quantity"""
        current = context.get('current_stock', 0)
        safety = context.get('safety_stock', 100)
        
        if current < safety:
            reorder_qty = safety - current + prediction
            return prediction, f"📦 REORDER: Need {reorder_qty:.0f} units immediately"
        return prediction, None
    
    def _suggest_discount(self, prediction: float, context: dict) -> Tuple[float, str]:
        """Suggest discount for overstock"""
        overstock = context.get('current_stock', 0) - prediction
        discount = min(30, 10 + int(overstock / 100))  # 10-30% discount
        return prediction, f"🏷️ OVERSTOCK: Offer {discount}% discount to move {overstock:.0f} units"
    
    def _apply_ramadan_boost(self, prediction: float, context: dict) -> Tuple[float, str]:
        """Apply Ramadan demand boost"""
        boosted = prediction * 1.4
        return boosted, "🌙 RAMADAN: Demand increased by 40%"
    
    def enforce_rules(self, predictions: List[float], context: dict) -> Dict:
        """Execute all dictator rules"""
        results = []
        actions = []
        
        for pred in predictions:
            modified_pred = pred
            alerts = []
            
            for rule in sorted(self.rules, key=lambda r: r.priority):
                if rule.condition({'predicted': modified_pred}, context):
                    modified_pred, alert = rule.action(modified_pred, context)
                    if alert:
                        alerts.append(alert)
                        actions.append({
                            'rule': rule.name,
                            'message': alert,
                            'priority': rule.priority
                        })
            
            results.append(modified_pred)
            self.action_history.extend(actions)
        
        return {
            'original': predictions,
            'modified': results,
            'actions': actions,
            'dictator_mode': len(actions) > 0
        }
    
    def get_stats(self) -> Dict:
        """Get dictator action statistics"""
        return {
            'total_actions': len(self.action_history),
            'actions_by_rule': {},
            'last_24h': [a for a in self.action_history[-10:]]
        }