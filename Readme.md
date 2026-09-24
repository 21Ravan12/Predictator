# 🚀 Predictator-v2

> *"Because spreadsheets are SO last decade"* 🤖

An ML-powered sales forecasting system that predicts product sales and enforces 
business rules through a **Dictator Engine** (don't worry — it's a benevolent 
dictator 😅).

Built as a learning project to explore the full lifecycle of a production-grade 
ML system: from data ingestion and feature engineering, through model training 
and serving, all the way to a modern web dashboard.

---

## ⚠️ Honest Status: Small on Purpose

This project is intentionally scoped small. I'm developing it on a modest 
laptop (literally a potato with a screen 🥔), so the dataset is tiny 
(3 products, ~180 days) and the infrastructure is deliberately simple.

**The goal isn't to fake scale — it's to get the architecture right first**, 
then grow into real data and real workloads.

What that means for the numbers you'll see:
- ✅ The end-to-end flow works (Frontend → Backend → gRPC → ML Engine → DB)
- ✅ Predictions are generated and displayed in a real dashboard
- ⚠️ The high R² (0.96) is on a small dataset — a signal, not a proof
- 🔜 Larger data, better validation, and cloud deployment are next

---

## 🎯 What It Does Today

- ✅ **Product-level sales forecasting** — predicts daily sales for individual products
- ✅ **Dictator Engine** — enforces business rules (floor limits, constraints)
- ✅ **Feature engineering** — 39 features including lags, rolling stats, cyclical encoding, holidays, and seasons
- ✅ **Flexible holiday & season banks** — CSV-driven, customizable per region
- ✅ **Tri-Core Architecture** — three independent services communicating via gRPC
- ✅ **Modern dashboard** — multi-page Next.js UI with charts and tables
- ✅ **Product catalog** — categories and products stored in PostgreSQL

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

| Layer | Technology |
|-------|------------|
| 🌐 Frontend | Next.js 15, TypeScript, Tailwind CSS, Recharts |
| ⚙️ Backend | NestJS, Prisma, PostgreSQL, JWT, gRPC client |
| 🧠 ML Engine | FastAPI, XGBoost, scikit-learn, Pandas, NumPy |
| 📡 Communication | gRPC (Protobuf) between Backend ↔ ML Engine |
| 🗄️ Databases | PostgreSQL (Backend), SQLite (ML Engine) |
| 🐳 DevOps | Docker, Git, GitHub |

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
npm run seed   # Seeds categories and products

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
| `/api/predictions/products` | GET | List products |
| `/api/predictions/categories` | GET | List categories |
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
      { "date": "2026-09-25", "predicted_sales": 63.65, "confidence_lower": 53.79, "confidence_upper": 73.51 }
    ],
    "summary": {
      "total_predicted": 441.40,
      "average_daily": 63.06,
      "peak_day": 68.85,
      "floor_violations": 0
    }
  }
}
```

---

## 🗺️ Roadmap

### ✅ Done
- [x] Product-level predictions with XGBoost
- [x] Dictator Engine (floor limits, constraints)
- [x] Feature engineering pipeline (39 features)
- [x] Holiday & season banks (CSV-driven, Baku-specific)
- [x] FastAPI REST API + gRPC server
- [x] NestJS backend with Prisma + PostgreSQL
- [x] JWT authentication scaffolding
- [x] Next.js dashboard with charts and tables
- [x] Product catalog with categories
- [x] Tri-Core gRPC communication

### 🔜 Next
- [ ] Larger dataset + proper train/validation split
- [ ] Category-level and store-level aggregation
- [ ] Weather API integration (real data)
- [ ] Promotion and price effect modeling
- [ ] Model retraining pipeline
- [ ] Automated tests (unit + e2e)
- [ ] Cloud deployment (Vercel + Railway + Neon)
- [ ] Monitoring & logging dashboard
- [ ] Docker Compose for one-command startup

### 🔮 Long-Term
- [ ] Support for big data workloads
- [ ] Real-time streaming predictions
- [ ] Multi-tenant architecture
- [ ] Advanced models (Prophet, LSTM, ensemble)

---

## 💡 Honest Reflections

A few things I've learned building this:

- **Architecture > algorithms at this stage.** A well-structured small system 
  is more valuable than a clever model bolted onto a mess.
- **gRPC is genuinely fast.** End-to-end requests through three services 
  complete in under a second.
- **Small data is humbling.** A high R² on 180 rows tells you the pipeline 
  works — not that the model is good.
- **Debugging is the job.** I've spent more hours fixing bugs than writing 
  new features, and that's exactly what real engineering looks like.

---

## 🤝 Contributing

This is currently a solo learning project, but I'm open to collaboration, 
feedback, or just a good conversation about ML engineering.

If you're interested, reach out! 🥰

---

## 📄 License

MIT — use it, break it, fix it, make it better! ✨
