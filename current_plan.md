# 📊 Predictator Roadmap v2

**Last Updated:** September 2026
**Philosophy:** Learn real-world ML by simulating production data pipelines — no paid APIs, just CSVs that teach us the format, then real integration later.

---

## ✅ DONE (Aug–Sep 2026)

### Architecture
- [x] Tri-Core Architecture (Next.js + NestJS + FastAPI)
- [x] gRPC communication between backend and ML engine
- [x] PostgreSQL + Prisma ORM
- [x] Redis-ready caching layer
- [x] JWT authentication framework
- [x] Docker Compose setup

### ML Engine
- [x] XGBoost model (R² ≈ 0.96 on small data)
- [x] 39 engineered features
- [x] Time, lag, rolling, seasonal features
- [x] Holiday bank (CSV-driven, 13 holidays)
- [x] Season bank (Baku-specific, 10 seasons)
- [x] Ramadan proximity features
- [x] Confidence intervals (RMSE-based)
- [x] Dictator Engine (floor limits)

### Backend (NestJS)
- [x] Products & Categories system
- [x] Prisma seeding from CSV
- [x] Prediction endpoints
- [x] Training endpoints
- [x] Health checks (DB, gRPC, cache)
- [x] Logging, exception filters, interceptors

### Frontend (Next.js)
- [x] Multi-page dashboard (Home, Predictions, Products, Settings)
- [x] Interactive charts (recharts)
- [x] Product catalog from PostgreSQL
- [x] Beautiful gradient UI with Tailwind

---

## 🎯 PHASE 1: Finish ML Engine Features

**Goal:** Complete the core ML engine with all features needed for real forecasting.

### 1.1 External Data Integration (CSV-Driven Learning)
Learn real data formats without paying for APIs:

- [ ] **Weather data CSV**
  - Format: date, temperature, humidity, precipitation, wind_speed, condition
  - Build a synthetic Baku weather dataset (2026, realistic patterns)
  - Feature engineering: temp lags, rainfall rolling windows, extreme weather flags
  - Later: swap CSV source for real API (OpenWeatherMap free tier)

- [ ] **Social media trends CSV**
  - Format: date, hashtag, mentions, sentiment_score, reach
  - Build sample data around product keywords (e.g., "electronics", "food")
  - Feature engineering: trend momentum, sentiment rolling averages, viral spikes
  - Later: swap for Twitter/Reddit API

- [ ] **Economic indicators CSV**
  - Format: month, gdp_index, inflation_rate, unemployment, consumer_confidence
  - Use real public data (World Bank, IMF — free)
  - Feature engineering: month-over-month deltas, seasonal adjustments

- [ ] **Promotions & price history CSV**
  - Format: date, product_id, promotion_flag, discount_pct, promotion_type
  - Build realistic promotion patterns
  - Feature engineering: days since/until promo, promo intensity, price elasticity

### 1.2 Multi-Level Predictions
- [ ] Category-level predictions (`/predict/category`)
- [ ] Store-level total predictions (`/predict/store`)
- [ ] Batch predictions (multiple products in one request)
- [ ] Hierarchical reconciliation (ensure category = sum of products)

### 1.3 Prediction Intelligence
- [ ] Feature importance API (`/features/{product_id}`)
- [ ] Model metrics API (`/metrics`)
- [ ] Prediction history (`/predictions/history`)
- [ ] Explainability endpoint (SHAP values)
- [ ] What-if analysis (`/predict/what-if`)

### 1.4 Data Pipeline
- [ ] Data validation on ingestion (schema + range checks)
- [ ] Feature store (persist computed features in PostgreSQL)
- [ ] Automated daily data refresh
- [ ] Backfill historical data on new product

**Deliverable:** ML engine handles weather, social, economic, promotion data from CSVs.

---

## 🔐 PHASE 2: Security & Optimization

**Goal:** Make the system production-ready.

### 2.1 Security
- [ ] Redis-based rate limiting (per-IP, per-endpoint)
- [ ] Input validation for ML (reject poisoned data)
- [ ] Model integrity check (hash verification on load)
- [ ] mTLS between NestJS and ML engine
- [ ] API versioning (`/api/v1/`)
- [ ] Audit logging for all predictions

### 2.2 Optimization
- [ ] Redis caching for predictions (TTL-based)
- [ ] Database indexes on hot queries
- [ ] Model quantization (smaller, faster XGBoost)
- [ ] Connection pooling for PostgreSQL
- [ ] Frontend code splitting & lazy loading
- [ ] Batch prediction optimization

**Deliverable:** 10x faster predictions, production-grade security.

---

## 🧠 PHASE 3: ML Depth

**Goal:** Move from "trained a model" to "engineered an ML system."

### 3.1 Model Improvements
- [ ] LightGBM (faster, often more accurate)
- [ ] Prophet (time-series-specific)
- [ ] Ensemble (XGBoost + Prophet + LightGBM)
- [ ] Hyperparameter tuning (Optuna)
- [ ] TimeSeriesSplit cross-validation

### 3.2 Production ML
- [ ] Model versioning (MLflow or custom)
- [ ] A/B testing framework (compare models live)
- [ ] Model drift detection
- [ ] Data drift detection
- [ ] Auto-retraining (scheduled + triggered)
- [ ] SHAP explainability for every prediction

**Deliverable:** Ensemble models with monitoring and explainability.

---

## 🚀 PHASE 4: Real Business Features

**Goal:** Turn predictions into decisions.

- [ ] Inventory optimization (reorder quantity suggestions)
- [ ] Anomaly detection (flag unusual sales)
- [ ] Seasonal decomposition visualization
- [ ] Forecast vs actual tracking
- [ ] Multi-format export (CSV, Excel, PDF)
- [ ] Real-time WebSocket updates
- [ ] Alert system (threshold-based)

**Deliverable:** Dashboard that suggests actions, not just numbers.

---

## ☁️ PHASE 5: Scale & Deploy

**Goal:** Ship it to the world.

- [ ] Full Docker Compose (all 3 services + PostgreSQL + Redis)
- [ ] Cloud deployment (Railway/Render)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Load testing (k6 or Locust)
- [ ] Public demo with sample data

**Deliverable:** Live public URL anyone can try.

---

## 📊 Success Metrics

### Model Performance
| Metric | Current | Target | Stretch |
|--------|---------|--------|---------|
| R² | 0.961 | 0.97 | 0.98 |
| MAE | ~6 | <5 | <3 |
| RMSE | ~10 | <8 | <6 |
| MAPE | TBD | <8% | <5% |

*Note: current R² is on a small dataset. Real evaluation needs more data.*

### System Performance
| Metric | Target |
|--------|--------|
| API response (cached) | <50ms |
| API response (uncached) | <500ms |
| Concurrent users supported | 100+ |
| Uptime | 99%+ |

---

## 🛠️ Tech Stack

### Current
- **Frontend:** Next.js 15, TypeScript, Tailwind, Recharts
- **Backend:** NestJS, Prisma, PostgreSQL, JWT
- **ML Engine:** FastAPI, XGBoost, Pandas, NumPy, gRPC
- **Database:** PostgreSQL (production), SQLite (ML engine local)
- **Communication:** gRPC (internal), REST (external)

### Planned Additions
- **Caching:** Redis
- **Monitoring:** Prometheus + Grafana
- **ML Tracking:** MLflow (or custom)
- **Explainability:** SHAP
- **Deployment:** Railway / Render / Fly.io

---

## 🎯 Guiding Principles

1. **CSV first, APIs later** — Learn data formats without paying.
2. **Real architecture, small data** — The pipeline matters more than the dataset size.
3. **Ship > Perfect** — Working beats waiting.
4. **Honest metrics** — Never claim more than the data proves.
5. **Modular by design** — Every piece replaceable.

---

## 📅 Timeline (Flexible)

| Phase | Focus | Duration |
|-------|-------|----------|
| 1 | ML Engine Features | 2–3 weeks |
| 2 | Security + Optimization | 2 weeks |
| 3 | ML Depth | 3 weeks |
| 4 | Business Features | 2 weeks |
| 5 | Scale & Deploy | 2 weeks |

**Total:** ~11 weeks (part-time)

---

**This roadmap is a living document. Update as we learn.**
