# 🚀 Predictator-v1

> *"Because spreadsheets are SO last decade"* 🤖

An ML-powered sales prediction engine that forecasts product sales and enforces business rules with the **Dictator Engine** (don't worry, it's a benevolent dictator 😅).

---

## 🎯 What It Does (So Far)

- ✅ **Product-level sales predictions** - Forecasts sales for individual products
- ✅ **Dictator enforcement** - Enforces business rules (floor limits, stock constraints)
- ✅ **Feature engineering** - Time features, lags, rolling statistics, holiday effects
- ✅ **API ready** - RESTful endpoints with FastAPI + Swagger docs
- ✅ **Database storage** - SQLite for data persistence

---

## 🚧 Current Status: WORK IN PROGRESS

> **I'm actively building this!** 🏗️

What I'm currently working on:
- 🔜 Adding more features (weather, promotions, price effects)
- 🔜 Category-level predictions
- 🔜 Store-level aggregation
- 🔜 Better models (XGBoost, Prophet)
- 🔜 Real weather API integration

---

## 🛠️ Tech Stack

| Tool | What It Does |
|------|--------------|
| 🐍 Python 3.10+ | The magic behind it all |
| ⚡ FastAPI | RESTful API framework |
| 🤖 Scikit-learn | Random Forest model |
| 🐼 Pandas | Data manipulation |
| 🗄️ SQLAlchemy + SQLite | Database management |
| 📊 NumPy | Number crunching |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/Predictator-v1.git
cd Predictator-v1/apps/ml-engine

# Create and activate virtual environment
python -m venv predictator_env
# Windows:
predictator_env\Scripts\activate
# Mac/Linux:
source predictator_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

Open Swagger docs: `http://localhost:8000/docs` 📚

---

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/train` | POST | Train/retrain the model |
| `/predict` | POST | Generate sales predictions |
| `/health` | GET | Check system status |

---

## 🎯 Sample Request

```json
POST /predict
{
  "product_id": "P001",
  "days_ahead": 7,
  "floor_limit": 150
}
```

---

## 🗺️ Roadmap

- [x] Basic product-level predictions
- [x] Dictator enforcement
- [x] API endpoints
- [ ] Weather data integration
- [ ] Category-level predictions
- [ ] Store-level aggregation
- [ ] XGBoost model
- [ ] Prophet model
- [ ] Dashboard & monitoring
- [ ] Docker deployment

---

## 🤝 Contributing

This is a solo project right now, but **I'm open to collaboration!** 

If you're interested, reach out! 🥰

---

## 📄 License

MIT — use it, break it, fix it, make it better! ✨
