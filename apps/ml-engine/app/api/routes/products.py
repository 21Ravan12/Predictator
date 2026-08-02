"""Product data endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from ...models import DatabaseManager
from ..dependencies import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
async def list_products(db: DatabaseManager = Depends(get_db)):
    """Get all products"""
    products = db.get_all_products()
    return {
        "success": True,
        "total": len(products),
        "products": products
    }


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    days_back: int = 90,
    db: DatabaseManager = Depends(get_db)
):
    """Get product data and statistics"""
    
    df = db.load_sales_history(product_id, days_back)
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    return {
        "success": True,
        "product_id": product_id,
        "records": len(df),
        "date_range": {
            "start": df['date'].min().strftime("%Y-%m-%d"),
            "end": df['date'].max().strftime("%Y-%m-%d")
        },
        "statistics": {
            "avg_sales": float(df['sales'].mean()),
            "max_sales": float(df['sales'].max()),
            "min_sales": float(df['sales'].min()),
            "total_sales": float(df['sales'].sum())
        },
        "recent_sales": df.tail(30).to_dict('records')
    }


@router.post("/{product_id}/seed")
async def seed_product_data(
    product_id: str,
    days: int = 90,
    db: DatabaseManager = Depends(get_db)
):
    """Seed sample data for a product"""
    
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
    np.random.seed(hash(product_id) % 2**32)
    
    base = np.random.uniform(50, 200)
    sales = base + np.random.normal(0, 20, len(dates))
    sales = np.maximum(sales, 10)
    
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'is_holiday': (dates.dayofweek >= 5)
    })
    
    db.save_sales_history(product_id, df)
    
    return {
        "success": True,
        "product_id": product_id,
        "message": f"Seeded {len(df)} days of data",
        "records": len(df)
    }


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Delete all data for a product"""
    
    deleted = db.clear_product_data(product_id)
    
    return {
        "success": True,
        "product_id": product_id,
        "deleted_records": deleted
    }


@router.post("/load-csv")
async def load_csv_data(
    csv_path: str,
    db: DatabaseManager = Depends(get_db)
):
    """Load product data from CSV file"""
    
    import pandas as pd
    
    try:
        df = pd.read_csv(csv_path)
        
        products_loaded = {}
        for product_id in df['product_id'].unique():
            product_df = df[df['product_id'] == product_id][['date', 'sales']]
            db.save_sales_history(str(product_id), product_df)
            products_loaded[str(product_id)] = len(product_df)
        
        return {
            "success": True,
            "message": "CSV data loaded successfully",
            "products_loaded": products_loaded,
            "total_records": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))