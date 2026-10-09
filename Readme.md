# 🚀 Predictator-v2

> *"Because spreadsheets are SO last decade"* 🤖

An ML-powered sales forecasting system that predicts product sales and enforces 
business rules through a **Dictator Engine** (don't worry — it's a benevolent 
dictator 😅).

Built as a learning project to explore the full lifecycle of a production-grade 
ML system: from data generation and feature engineering, through model training 
and serving, all the way to a modern web dashboard.

---

## ⚠️ Honest Status: Synthetic Data, Real Pipeline

This project runs on **synthetic data**, and that's on purpose. My laptop is 
basically a potato with a screen 🥔, so instead of waiting for real retail 
data, I generated a realistic 2-year dataset for an imaginary Baku store 
("BakuMart") — 40 products across 4 categories, with weather, holidays, 
Ramadan effects, and promotions baked in.

**The goal isn't to fake scale — it's to get the architecture right, then 
swap in real data later.**

What that means for the numbers you'll see:
- ✅ The end-to-end flow works (Frontend → Backend → gRPC → ML Engine → DB)
- ✅ Predictions are generated, served, and displayed in a real dashboard
- ✅ 40 products, 4 categories, 29,200 rows of sales history
- ⚠️ High R² (0.997) is on synthetic data — a signal, not a proof
- 🔜 Real data integration, cloud deployment, and monitoring are next

---

## 🎯 What It Does Today

- ✅ **Product-level sales forecasting** — predicts daily sales for 40 products
- ✅ **Dictator Engine** — enforces business rules (floor limits, constraints)
- ✅ **53 engineered features** — lags, rolling stats, cyclical encoding, weather, 
  holidays, Ramadan, promotions
- ✅ **Synthetic data generator** — 2 years of realistic sales patterns
- ✅ **Tri-Core Architecture** — Next.js + NestJS + FastAPI communicating via gRPC
- ✅ **Modern admin dashboard** — multi-page Next.js UI with charts, tables, and search
- ✅ **Product catalog** — 40 products, 4 categories stored in PostgreSQL
- ✅ **XGBoost model** — R² 0.997, MAE 1.62, RMSE 4.40 on synthetic data

---

## 🚧 Current Status: WORK IN PROGRESS

> **I'm actively building this!** 🏗️

What I'm currently working on:
- 🔜 Category-level and store-level aggregation
- 🔜 SHAP explainability for predictions
- 🔜 Real weather API integration (currently synthetic)
- 🔜 Redis caching for faster repeated predictions
- 🔜 Cloud deployment (Vercel + Railway + Neon)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| 🌐 Frontend | Next.js 15, TypeScript, Tailwind CSS, Recharts |
| ⚙️ Backend | NestJS, Prisma, PostgreSQL, JWT, gRPC client |
| 🧠 ML Engine | FastAPI, XGBoost, scikit-learn, Pandas, NumPy |
| 📡 Communication | gRPC (Protobuf) between Backend ↔ ML Engine |
| 🗄️ Databases | PostgreSQL (Backend), SQLite (ML Engine) |
| 🐳 DevOps | Docker, Git, GitHub |

---

## 📊 Dataset Overview

The dataset simulates a 2-year period for **BakuMart**, a mid-sized retail store.

| Metric | Value |
|--------|-------|
| 🏪 Store | BakuMart (Baku, Azerbaijan) |
| 📅 Date range | 2025-01-01 → 2026-12-31 |
| 📦 Products | 40 (across 4 categories) |
| 📁 Categories | Electronics (12), Food (14), Clothing (8), Home & Garden (6) |
| 📊 Sales rows | 29,200 |
| 🎉 Holidays | 50 (2 years) |
| 🕌 Ramadan periods | 2 |
| 💰 Promotions | ~1,460 events |

Patterns baked into the data:
- Weekly seasonality (weekends higher)
- Monthly/seasonal trends per category
- Holiday spikes (Novruz, Victory Day, New Year)
- Ramadan effect (Food ↑, others ↓)
- Weather effects (rain → Clothing ↓, Food ↑)
- Promotion effects (~5% of days)
- Occasional outliers and stockouts

---

## 🚀 Quick Start

Each service runs independently. Open three terminals.

### 1️⃣ ML Engine (FastAPI + gRPC)

```bash
cd apps/ml-engine
python -m venv predictator_env

# Windows
predictator_env\Scripts\activate
# Mac/Linux
source predictator_env/bin/activate

pip install -r requirements.txt

# Generate gRPC code (first time only)
python -m grpc_tools.protoc -I=./app/grpc/proto \
  --python_out=./app/grpc/generated \
  --grpc_python_out=./app/grpc/generated \
  ./app/grpc/proto/predictor.proto

# Generate synthetic dataset (first time only)
python scripts/generate_promotions.py
python scripts/generate_sales.py

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Swagger: http://localhost:8000/docs  
✅ gRPC: localhost:50051

### 2️⃣ Backend (NestJS + PostgreSQL)

```bash
cd apps/backend
npm install

# Configure database
echo "DATABASE_URL=postgresql://user:password@localhost:5432/predictator" > .env
echo "JWT_SECRET=change-me" >> .env
echo "ML_ENGINE_GRPC_URL=localhost:50051" >> .env

# Set up database
npx prisma generate
npx prisma migrate dev --name init
npm run seed   # Seeds 4 categories + 40 products

# Run
npm run start:dev
```

✅ API: http://localhost:4000/api  
✅ Health: http://localhost:4000/api/health

### 3️⃣ Frontend (Next.js)

```bash
cd apps/frontend
npm install

echo "NEXT_PUBLIC_API_URL=http://localhost:4000/api" > .env.local

npm run dev
```

✅ Dashboard: http://localhost:3000

---

## 📋 API Overview

### ML Engine (FastAPI)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/train` | POST | Train / retrain the model |
| `/predict` | POST | Generate sales predictions |
| `/health` | GET | Service + gRPC status |

### Backend (NestJS)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/predictions` | POST | Get predictions (proxies to ML Engine via gRPC) |
| `/api/predictions/products` | GET | List all products |
| `/api/predictions/categories` | GET | List all categories |
| `/api/predictions/status` | GET | Model status |
| `/api/health` | GET | Full system health |

---

## 🎯 Sample Request

```bash
curl -X POST http://localhost:4000/api/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "P001",
    "daysAhead": 7,
    "floorLimit": 0
  }'
```

Response (simplified):

```json
{
  "success": true,
  "data": {
    "product_id": "P001",
    "predictions": [
      { "date": "2026-10-10", "predicted_sales": 11.99, "confidence_lower": 7.58, "confidence_upper": 16.39 }
    ],
    "summary": {
      "total_predicted": 80.28,
      "average_daily": 11.47,
      "peak_day": 12.57,
      "floor_violations": 0
    }
  }
}
```

---

## 🗺️ Roadmap

### ✅ Done
- [x] Synthetic dataset generator (29,200 rows, 40 products)
- [x] XGBoost model (R² 0.997, MAE 1.62, RMSE 4.40)
- [x] 53 engineered features (time, lag, rolling, weather, holiday, promotion)
- [x] Dictator Engine (floor limits, constraints)
- [x] FastAPI REST API + gRPC server
- [x] NestJS backend with Prisma + PostgreSQL
- [x] Product catalog (40 products, 4 categories)
- [x] JWT authentication scaffolding
- [x] Next.js admin dashboard with charts, tables, search
- [x] Tri-Core gRPC communication
- [x] Bug fix: prediction placeholder values (median instead of 0)

### 🔜 Next
- [ ] Category-level and store-level aggregation
- [ ] SHAP explainability per prediction
- [ ] Redis caching for faster repeated predictions
- [ ] Real weather API integration
- [ ] Prediction vs actual backtesting view
- [ ] Automated tests (unit + e2e)
- [ ] Cloud deployment (Vercel + Railway + Neon)
- [ ] Docker Compose for one-command startup

### 🔮 Long-Term
- [ ] Real retail data integration
- [ ] Multi-tenant architecture
- [ ] Advanced models (Prophet, LSTM, ensemble)
- [ ] Real-time streaming predictions

---

## 💡 Honest Reflections

A few things I've learned building this:

- **Architecture > algorithms at this stage.** A well-structured small system 
  is more valuable than a clever model bolted onto a mess.
- **Data quality beats model choice.** Going from 180 rows to 29,200 rows 
  improved R² more than any hyperparameter tuning did.
- **gRPC is genuinely fast.** End-to-end requests across three services 
  complete in well under a second.
- **Debugging is the job.** The most educational moment was finding a 
  prediction bug where future rows had `sales=0`, which distorted feature 
  engineering and caused 3x underprediction. The fix was small; finding 
  it was the work.
- **UI consistency matters.** Turning a prototype UI into a proper admin 
  panel changed how the whole project feels.

---

## 🤝 Contributing

This is currently a solo learning project, but I'm open to collaboration, 
feedback, or just a good conversation about ML engineering.

If you're interested, reach out! 🥰

---

## 📄 License

MIT — use it, break it, fix it, make it better! ✨
