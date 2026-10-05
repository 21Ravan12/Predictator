"""Generate synthetic sales data for BakuMart

Creates ~29,200 rows (40 products × 730 days) with:
- Realistic patterns (trend, weekly, seasonal)
- Weather effects (generated on-the-fly)
- Holiday spikes
- Ramadan effects
- Promotion effects
- Product-specific personalities

Output: data/raw/sales_data_large.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

np.random.seed(42)

# ============================================
# 🎯 CONFIG
# ============================================

START_DATE = '2025-01-01'
END_DATE = '2026-12-31'
STORE_ID = 'ST001'

# ============================================
# 📦 LOAD DATA
# ============================================

products = pd.read_csv('data/raw/products.csv')
holidays = pd.read_csv('data/raw/holidays_baku.csv')
promotions = pd.read_csv('data/raw/promotions.csv')

print(f"✅ Loaded {len(products)} products")
print(f"✅ Loaded {len(holidays)} holidays")
print(f"✅ Loaded {len(promotions)} promotions")

# ============================================
# 📅 DATES
# ============================================

dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
print(f"📅 Generating {len(dates)} days")

# ============================================
# 🌤️ WEATHER GENERATOR
# ============================================

def generate_weather(date):
    """Generate realistic Baku weather for a date"""
    month = date.month

    month_temps = {
        1: 4, 2: 5, 3: 9, 4: 14, 5: 20, 6: 25,
        7: 28, 8: 28, 9: 24, 10: 18, 11: 12, 12: 7
    }
    base_temp = month_temps[month]
    temp = round(base_temp + np.random.normal(0, 3), 1)

    humidity = np.random.randint(55, 85) if month in [11, 12, 1, 2, 3] else np.random.randint(40, 70)

    is_rainy_season = month in [3, 4, 5, 10, 11]
    rain_prob = 0.35 if is_rainy_season else 0.15
    precipitation = round(np.random.exponential(2.5), 1) if np.random.random() < rain_prob else 0.0

    wind = round(np.random.uniform(5, 20), 1)

    if precipitation > 3:
        condition = 'Rainy'
    elif precipitation > 0.5:
        condition = 'Cloudy'
    elif humidity > 75:
        condition = 'Cloudy'
    else:
        condition = 'Sunny'

    pressure = np.random.randint(1008, 1025)

    return {
        'temperature': temp,
        'humidity': humidity,
        'precipitation': precipitation,
        'wind_speed': wind,
        'condition': condition,
        'pressure': pressure,
    }

# ============================================
# 🕌 RAMADAN CHECK
# ============================================

RAMADAN_PERIODS = [
    ('2025-03-01', '2025-03-30'),
    ('2026-02-18', '2026-03-19'),
]

def is_ramadan(date):
    for start, end in RAMADAN_PERIODS:
        if pd.Timestamp(start) <= pd.Timestamp(date) <= pd.Timestamp(end):
            return True
    return False

# ============================================
# 🎉 HOLIDAY LOOKUP
# ============================================

holiday_lookup = {}
for h in holidays.itertuples():
    holiday_lookup[h.date] = {
        'name': h.holiday_name,
        'multiplier': h.multiplier,
        'category': h.category_affected,
    }

# ============================================
# 💰 PROMO LOOKUP
# ============================================

promo_lookup = {}
for p in promotions.itertuples():
    date_range = pd.date_range(start=p.start_date, end=p.end_date)
    for d in date_range:
        key = f"{p.product_id}_{d.strftime('%Y-%m-%d')}"
        promo_lookup[key] = {
            'type': p.promo_type,
            'discount': p.discount_percent,
            'promo_price': p.promo_price,
        }

print(f"✅ Promo lookup built: {len(promo_lookup)} product-days")

# ============================================
# 📊 GENERATE SALES
# ============================================

all_sales = []
total_rows = len(products) * len(dates)

print(f"\n🔄 Generating {total_rows} rows...")

for i, product in enumerate(products.itertuples()):
    print(f"   [{i+1}/{len(products)}] {product.product_id} - {product.name}")

    for date in dates:
        date_str = date.strftime('%Y-%m-%d')

        # 1. Base sales
        base = product.base_sales

        # 2. Long-term trend (+15% over period)
        days_since_start = (date - dates[0]).days
        trend = 1 + (days_since_start / len(dates)) * 0.15

        # 3. Weekly pattern (+15% weekends)
        day_of_week = date.dayofweek
        weekly = 1.15 if day_of_week >= 5 else 1.0

        # 4. Seasonal pattern
        month = date.month
        if product.seasonality == 'Winter':
            seasonal = 1 + 0.3 * np.cos(2 * np.pi * (month - 1) / 12)
        elif product.seasonality == 'Summer':
            seasonal = 1 + 0.3 * np.cos(2 * np.pi * (month - 7) / 12)
        elif product.seasonality == 'Spring':
            seasonal = 1 + 0.25 * np.cos(2 * np.pi * (month - 4) / 12)
        elif product.seasonality == 'Ramadan':
            seasonal = 1.0 + 0.2 * (1 if is_ramadan(date) else 0)
        else:  # Stable
            seasonal = 1.0

        # 5. Holiday effect
        holiday_mult = 1.0
        holiday_name = 'None'
        if date_str in holiday_lookup:
            h = holiday_lookup[date_str]
            holiday_name = h['name']
            if h['category'] == 'All' or h['category'] == product.category:
                holiday_mult = h['multiplier']
            else:
                holiday_mult = 1.0 + (h['multiplier'] - 1.0) * 0.3

        # 6. Weather effect
        weather = generate_weather(date)
        weather_mult = 1.0

        if product.category == 'Clothing':
            if weather['temperature'] < 10: weather_mult *= 1.15
            if weather['temperature'] > 28: weather_mult *= 0.90
            if weather['precipitation'] > 3: weather_mult *= 0.85
        elif product.category == 'Food':
            if weather['precipitation'] > 3: weather_mult *= 1.05
        else:  # Electronics, Home
            if weather['precipitation'] > 3: weather_mult *= 0.92

        # 7. Ramadan effect
        ramadan_mult = 1.0
        if is_ramadan(date):
            if product.category == 'Food':
                ramadan_mult = 1.25
            elif product.category == 'Home & Garden':
                ramadan_mult = 1.10
            else:
                ramadan_mult = 0.95

        # 8. Promotion effect
        promo_key = f"{product.product_id}_{date_str}"
        promo_mult = 1.0
        promo_type = 'None'
        discount = 0
        is_promo = False

        if promo_key in promo_lookup:
            promo = promo_lookup[promo_key]
            is_promo = True
            promo_type = promo['type']
            discount = promo['discount']
            promo_mult = 1 + (discount / 100) * 1.5

        # 9. Calculate sales
        sales = base * trend * weekly * seasonal * holiday_mult * weather_mult * ramadan_mult * promo_mult

        # 10. Add noise
        noise = np.random.normal(0, product.volatility * base * 0.3)
        sales = max(1, sales + noise)

        # 11. Occasional outliers (2%)
        if np.random.random() < 0.02:
            sales *= np.random.uniform(1.5, 2.5)

        # 12. Rare stockouts (0.5%)
        if np.random.random() < 0.005:
            sales = max(1, sales * 0.2)

        # Determine event type
        if holiday_name != 'None':
            event_type = 'Holiday'
        elif is_ramadan(date):
            event_type = 'Ramadan'
        elif is_promo:
            event_type = 'Promotion'
        else:
            event_type = 'Normal'

        # Season name
        if month in [12, 1, 2]:
            season = 'Winter'
        elif month in [3, 4, 5]:
            season = 'Spring'
        elif month in [6, 7, 8]:
            season = 'Summer'
        else:
            season = 'Autumn'

        all_sales.append({
            'date': date_str,
            'store_id': STORE_ID,
            'product_id': product.product_id,
            'category': product.category,
            'sales': round(sales, 0),
            'price': round(product.unit_price, 2),
            'discount_percent': discount if is_promo else 0,
            'promo_price': promo_lookup.get(promo_key, {}).get('promo_price', product.unit_price) if is_promo else product.unit_price,
            'holiday_name': holiday_name,
            'season_name': season,
            'event_type': event_type,
            'is_promo': 1 if is_promo else 0,
            'temperature': weather['temperature'],
            'humidity': weather['humidity'],
            'precipitation': weather['precipitation'],
            'wind_speed': weather['wind_speed'],
            'weather_condition': weather['condition'],
            'pressure': weather['pressure'],
        })

# ============================================
# 💾 SAVE
# ============================================

df = pd.DataFrame(all_sales)
output_path = 'data/raw/sales_data_large.csv'
df.to_csv(output_path, index=False)

print(f"\n" + "="*60)
print(f"🎉 SALES DATA GENERATED")
print(f"="*60)
print(f"📊 Total rows:      {len(df):,}")
print(f"📦 Products:        {df['product_id'].nunique()}")
print(f"📁 Categories:      {df['category'].nunique()}")
print(f"📅 Date range:      {df['date'].min()} → {df['date'].max()}")
print(f"💰 Promo days:      {(df['is_promo'] == 1).sum():,}")
print(f"🎉 Holiday days:    {(df['event_type'] == 'Holiday').sum():,}")
print(f"🕌 Ramadan days:    {(df['event_type'] == 'Ramadan').sum():,}")
print(f"💾 Saved to:        {output_path}")
print(f"="*60)

print(f"\n📊 Sales by category:")
print(df.groupby('category')['sales'].agg(['mean', 'min', 'max']).round(1))

print(f"\n📊 Event type distribution:")
print(df['event_type'].value_counts())