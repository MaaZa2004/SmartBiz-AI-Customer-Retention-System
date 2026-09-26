# SmartBiz AI — Customer Retention & Decision Intelligence System

An AI-powered decision intelligence platform for e-commerce businesses. It predicts customer churn, segments customers by behavior, forecasts category-level sales, and turns those signals into concrete, prioritized retention actions.

## What it does

- **Churn Prediction** — Logistic Regression model estimates the probability a customer will churn and classifies them as Low / Medium / High risk.
- **Customer Segmentation** — K-Means clustering groups customers into Premium, Regular, or Low-Value tiers based on tenure, spending, satisfaction, and address data.
- **Sales Forecasting** — Random Forest model projects expected sales value per product category and flags trend direction (Upward / Stable / Downward).
- **Decision Engine** — Combines churn risk, segment, and sales trend into a weighted priority score, then outputs a specific, human-readable recommended action (e.g. "issue a 15% retention discount" vs. "include in standard newsletter campaign").
- **What-If Simulator** — Test hypothetical customer profiles against all three models without writing anything to the database.
- **Reports** — Export executive PDF and Excel reports summarizing churn rate, revenue, and high-priority recommendations.

## Architecture

```
┌─────────────┐      REST API       ┌──────────────┐      SQLAlchemy      ┌────────────┐
│   React     │ ──────────────────> │   FastAPI    │ ───────────────────> │  Database  │
│  (Vite,     │ <────────────────── │   Backend    │ <─────────────────── │ (SQLite /  │
│  Tailwind)  │      JSON / JWT     │              │                      │  MySQL)    │
└─────────────┘                     └──────┬───────┘                      └────────────┘
                                            │
                                            ▼
                                  ┌───────────────────┐
                                  │  Scikit-learn ML   │
                                  │  models (.pkl)      │
                                  │  Churn / Segment /   │
                                  │  Forecast            │
                                  └───────────────────┘
```

- **Backend**: FastAPI, SQLAlchemy 2.0, JWT authentication (role-based: Admin / Manager / Business Analyst), scikit-learn for inference
- **Frontend**: React 19, Vite, Tailwind CSS, Recharts
- **Database**: SQLite by default for local development; MySQL supported via `DATABASE_URL`
- **ML models**: trained offline on a Kaggle e-commerce churn dataset, serialized with `joblib`, loaded at API startup

## Getting started

### Prerequisites
- Python 3.12+
- Node.js 18+

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example environment file and fill in real values:

```bash
cp .env.example .env
```

Generate a secret key and set it in `.env`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

No database setup is required to get started — the app falls back to a local SQLite file (`smartbiz_dev.db`) automatically if `DATABASE_URL` is not set.

Run the server:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`.

### First run

1. Register an account via the UI, or `POST /api/auth/register`
2. Log in
3. Click **Seed DB** on the Analytics Dashboard to load sample customer data (from the Kaggle churn dataset)
4. Explore the Dashboard, Customers Database, and Churn Simulator

## Environment variables

See `backend/.env.example` for the full list. Required:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing secret — must be set, no fallback | *(none — app refuses to start without it)* |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./smartbiz_dev.db` |
| `BACKEND_CORS_ORIGINS` | Comma-separated list of allowed frontend origins | `http://localhost:3000,http://127.0.0.1:3000` |

## Running tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -q
```

## Model training

Trained model artifacts are already included under `backend/ml/saved_models/`. To retrain from scratch:

```bash
cd backend
python ml/training/train_churn.py
python ml/training/train_segment.py
python ml/training/train_forecast.py
```

Each script prints evaluation metrics (accuracy, ROC-AUC / RMSE / R²) after training.

## API overview

| Endpoint | Method | Description | Access |
|---|---|---|---|
| `/api/auth/register` | POST | Create an account | Public |
| `/api/auth/login` | POST | Get access/refresh tokens | Public |
| `/api/customers/` | GET | List customers | Any authenticated user |
| `/api/customers/seed` | POST | Load sample dataset | Admin / Manager |
| `/api/predict/churn` | POST | Predict churn for an existing customer | Any authenticated user |
| `/api/predict/segment` | POST | Segment an existing customer | Any authenticated user |
| `/api/predict/forecast` | POST | Forecast category sales | Admin / Business Analyst |
| `/api/predict/simulate` | POST | Run full pipeline on hypothetical data (no persistence) | Any authenticated user |
| `/api/decision-engine/recommend` | POST | Get a prioritized recommendation for a customer | Any authenticated user |
| `/api/reports/export` | GET | Export PDF or Excel report | Any authenticated user |

Full interactive documentation is available at `/docs` once the backend is running.

## Known limitations

- ML models are trained on a static, public Kaggle dataset rather than live business data — predictions are illustrative, not tuned to any specific real business
- No automated retraining pipeline; models must be retrained manually as data changes
- Decision Engine recommendations are rule-based text templates, not outcome-optimized
- SQLite (default) is suitable for development only; use MySQL/PostgreSQL for any real deployment

## Tech stack

**Backend**: FastAPI · SQLAlchemy · Pydantic · scikit-learn · pandas · JWT (python-jose) · slowapi (rate limiting) · reportlab · openpyxl

**Frontend**: React · Vite · Tailwind CSS · Recharts · lucide-react

## License

MIT
