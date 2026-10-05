"""Generate promotions for BakuMart products

Creates ~1,460 promotion events across 40 products over 730 days.

Output: data/raw/promotions.csv
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
PROMO_PROBABILITY = 0.05  # 5% of days get a promo

# ============================================
# 📦 LOAD PRODUCTS
# ============================================

products = pd.read_csv('data/raw/products.csv')
print(f"✅ Loaded {len(products)} products")

# ============================================
# 🎯 PROMO TYPES
# ============================================

PROMO_TYPES = [
    {'type': 'Percentage', 'min_discount': 10, 'max_discount': 30},
    {'type': 'BOGO', 'min_discount': 50, 'max_discount': 50},
    {'type': 'Fixed', 'min_discount': 5, 'max_discount': 20},
    {'type': 'Bundle', 'min_discount': 15, 'max_discount': 25},
    {'type': 'Flash Sale', 'min_discount': 30, 'max_discount': 50},
]

# ============================================
# 📅 DATE RANGE
# ============================================

dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
print(f"📅 Date range: {len(dates)} days")

# ============================================
# 🎯 GENERATE PROMOS
# ============================================

promotions = []

for product in products.itertuples():
    for date in dates:
        # Random chance of promotion
        if np.random.random() < PROMO_PROBABILITY:
            # Pick promo type
            promo_type = np.random.choice(PROMO_TYPES)

            # Random discount within range
            discount = np.random.uniform(
                promo_type['min_discount'],
                promo_type['max_discount']
            )

            # Calculate promo price
            promo_price = product.unit_price * (1 - discount / 100)

            # Duration: 1-5 days
            duration = np.random.randint(1, 6)

            promotions.append({
                'product_id': product.product_id,
                'start_date': date.strftime('%Y-%m-%d'),
                'end_date': (date + timedelta(days=duration-1)).strftime('%Y-%m-%d'),
                'promo_type': promo_type['type'],
                'discount_percent': round(discount, 1),
                'original_price': round(product.unit_price, 2),
                'promo_price': round(promo_price, 2),
                'duration_days': duration,
            })

# ============================================
# 💾 SAVE
# ============================================

df = pd.DataFrame(promotions)
df = df.sort_values('start_date').reset_index(drop=True)

output_path = 'data/raw/promotions.csv'
df.to_csv(output_path, index=False)

print(f"\n✅ Generated {len(df)} promotions")
print(f"💾 Saved to {output_path}")

# Summary
print(f"\n📊 Promotions by type:")
print(df['promo_type'].value_counts())

print(f"\n📊 Promotions by product (top 10):")
print(df['product_id'].value_counts().head(10))

print(f"\n📊 Promotions by year:")
df['year'] = pd.to_datetime(df['start_date']).dt.year
print(df['year'].value_counts().sort_index())