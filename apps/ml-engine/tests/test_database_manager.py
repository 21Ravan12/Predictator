import pandas as pd
from datetime import datetime, timedelta

from app.models.database import DatabaseManagerV2


def test_database_manager_supports_prediction_flow(tmp_path):
    db_path = tmp_path / "predictor.db"
    db = DatabaseManagerV2(str(db_path))

    dates = [datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=1)]
    df = pd.DataFrame({
        "date": dates,
        "sales": [10.0, 12.0],
        "is_holiday": [False, False],
    })

    db.save_sales_history("product-1", df)
    history = db.load_sales_history("product-1", days_back=30)

    assert len(history) == 2
    assert history["sales"].tolist() == [10.0, 12.0]

    db.log_prediction("product-1", [{"date": datetime.now().strftime("%Y-%m-%d"), "predicted_sales": 11.0}], 5)
    history_rows = db.get_prediction_history("product-1", days_back=30)

    assert len(history_rows) == 1
    assert history_rows[0]["product_id"] == "product-1"
