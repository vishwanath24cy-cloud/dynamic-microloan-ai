# AI-Based Dynamic Microloan Repayment & Cash-Flow Planner

An intelligent financial inclusion platform designed for microloan borrowers. The system forecasts borrower cash flows and dynamically adapts repayment schedules, minimizing defaults while protecting borrower liquidity.

---

## Project Structure

```text
dynamic-microloan-ai/
├── frontend/          # React + Vite web dashboard
│   ├── src/           # React components (App.jsx, styles)
│   ├── package.json   # Frontend scripts and dependencies
│   └── vite.config.js # Vite build configuration
├── backend/           # FastAPI backend service
│   ├── app/
│   │   ├── main.py        # FastAPI application with CORS & /health
│   │   ├── database.py    # SQLAlchemy engine & SQLite connection
│   │   ├── models.py      # Relational ORM models (6 tables)
│   │   ├── schemas.py     # Pydantic response models
│   │   ├── seed.py        # 5 distinct borrower scenario generator
│   │   └── routers/
│   │       └── borrowers.py # REST API endpoints
│   └── requirements.txt   # Backend Python dependencies
├── ml/                # Machine learning models & prediction stubs
│   ├── predictor_stub.py # Baseline cash-flow repayment predictor
│   └── README.md
├── data/              # SQLite database storage & dataset assets
│   ├── microloans.db  # SQLite database (auto-created on backend startup)
│   └── README.md
├── requirements.txt   # Global Python dependencies
└── README.md          # Project documentation & run guide
```

---

## Technology Stack

- **Frontend**: React 18, Vite
- **Backend**: Python 3.13+, FastAPI, Uvicorn, SQLAlchemy 2.0
- **Machine Learning**: Python (scikit-learn, numpy, pandas ready)
- **Database**: SQLite3 (relational schema with cascading foreign keys)

---

## Database Schema (SQLite)

The database consists of 6 interconnected tables:

1. **`borrowers`**: `borrower_id` (PK), `name`, `age`, `occupation`
2. **`loans`**: `loan_id` (PK), `borrower_id` (FK), `loan_amount`, `emi_amount`, `loan_start_date`, `repayment_frequency`
3. **`transactions`**: `transaction_id` (PK), `borrower_id` (FK), `date`, `income`, `expenses`, `cash_balance`
4. **`repayments`**: `repayment_id` (PK), `borrower_id` (FK), `date`, `amount`, `days_late`, `status`
5. **`predictions`**: `prediction_id` (PK), `borrower_id` (FK), `prediction_date`, `predicted_income`, `predicted_expenses`, `predicted_available_cash`
6. **`recommendations`**: `recommendation_id` (PK), `borrower_id` (FK), `recommendation`, `stress_level`, `persistent_stress`, `reason`, `created_at`

---

## Demo Borrowers & Scenarios

The backend automatically seeds 5 realistic synthetic borrower profiles on startup if the database is empty:

- **Borrower A (Aarav Sharma - Grocery Owner)**:
  - *Scenario*: Stable income and expenses → **LOW stress** (`persistent_stress = False`).
- **Borrower B (Bhavna Patel - Textile Weaver)**:
  - *Scenario*: Temporary raw material bottleneck / income dip → **MEDIUM temporary stress** (`persistent_stress = False`).
- **Borrower C (Chirag Verma - Delivery Driver)**:
  - *Scenario*: High stress for 2 consecutive months following vehicle repair → **HIGH stress, PERSISTENT STRESS** (`persistent_stress = True`).
- **Borrower D (Deepika Nair - Produce Trader)**:
  - *Scenario*: Seasonal lean sowing period followed by harvest revenue surge → **LOW stress (recovered)** (`persistent_stress = False`).
- **Borrower E (Eshwar Rao - Cafeteria Operator)**:
  - *Scenario*: Continuous 4-month income decline and repeated missed payments → **SEVERE stress, PERSISTENT STRESS** (`persistent_stress = True`).

---

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health & SQLite connectivity check |
| `GET` | `/` | API status and root links |
| `GET` | `/api/borrowers` | List all borrowers with aggregated loan totals & stress levels |
| `GET` | `/api/borrowers/{id}` | Full profile including loans, transactions, repayments, predictions, & recommendations |
| `GET` | `/api/borrowers/{id}/loans` | Loans associated with the borrower |
| `GET` | `/api/borrowers/{id}/transactions` | Chronological cash-flow transaction records |
| `GET` | `/api/borrowers/{id}/repayments` | Repayment and delinquency history |
| `GET` | `/api/borrowers/{id}/predictions` | Cash-flow forecast records |
| `GET` | `/api/borrowers/{id}/recommendations` | Dynamic repayment suggestions and stress assessments |
| `GET` | `/api/dashboard/summary` | Portfolio KPIs and stress distribution breakdown |
| `POST` | `/api/seed` | Force reset and re-seed demo data (`?force=true`) |

---

## Quickstart Guide

### 1. Backend Setup & Run

Navigate to `backend/`:
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

- API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 2. Frontend Setup & Run

Navigate to `frontend/`:
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

### 3. Verify Database and Endpoints

Run the automated test suite in `backend/`:
```bash
cd backend
python test_db_and_api.py
```
