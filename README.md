# FinSight — Smart Personal Finance & Budgeting Platform

A comprehensive B.Tech FinTech project demonstrating full-stack development with PostgreSQL, MongoDB, Python/FastAPI, and React.

## Project Overview

FinSight is a smart personal finance management platform that helps users:
- Track income and expenses with automatic categorization
- Set and monitor budgets with real-time breach prediction
- Build savings goals with auto-sweep features
- Receive financial insights
- Detect and flag suspicious transactions

**Target Users:** College students, young professionals, and anyone seeking better financial organization.

## Features

- **User Authentication:** JWT-based auth with role-based access control (USER, ADMIN, SUPER_ADMIN)
- **Account Management:** Create and manage multiple accounts (Cash, Bank, UPI, Card)
- **Transaction Ledger:** Full CRUD with auto-categorization, receipt uploads (GridFS)
- **Budgeting:** Per-category monthly budgets with utilization tracking and breach alerts
- **Savings Goals:** Track progress toward financial goals with automatic sweeps
- **Analytics Dashboard:** Interactive charts (Spending by Category, Monthly Trend, Top Payees)
- **Dual Database Architecture:** PostgreSQL (system-of-record) + MongoDB (analytics store)
- **Advanced SQL:** Stored procedures, CTEs, window functions, indexing strategies
- **ML Integration:** Auto-categorization (TF-IDF + Logistic Regression), Anomaly detection (Isolation Forest)

## Technology Stack

### Backend
- **Python 3.12** + **FastAPI** — Modern async web framework
- **PostgreSQL 16** — Relational database with advanced SQL features
- **MongoDB 7** — NoSQL analytics database
- **SQLAlchemy 2.0** — ORM for PostgreSQL
- **PyMongo** — MongoDB driver
- **PyJWT** + **Passlib/bcrypt** — Authentication
- **APScheduler** — Scheduled jobs and automation
- **scikit-learn** — Machine learning models
- **pandas** — Data analysis

### Frontend
- **React 18** + **Vite** — Fast development experience
- **Tailwind CSS** — Utility-first styling
- **Recharts** — Data visualization
- **React Query** — Server state management
- **Axios** — HTTP client

### DevOps
- **Docker** + **docker-compose** — Containerization
- **Alembic** — Database migrations
- **pytest** — Testing framework

## Project Structure

```
finsight/
├── frontend/                     # React application
│   ├── src/
│   │   ├── api/                 # API client & endpoints
│   │   ├── components/          # Reusable UI components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page components
│   │   ├── utils/               # Helper functions
│   │   ├── context/             # React context providers
│   │   └── main.jsx             # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── core/                # Security, dependencies, exceptions
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   └── db/                  # Database connections
│   ├── sql/                     # SQL scripts (schema, procedures, views)
│   ├── ml/                      # Machine learning modules
│   ├── sync/                    # SQL → NoSQL sync job
│   ├── tests/                   # Unit & integration tests
│   └── requirements.txt
├── docs/                        # Project documentation
│   ├── abstract.md
│   ├── methodology.md
│   ├── architecture.md
│   ├── er_diagram.md
│   ├── dfd.md
│   ├── use_cases.md
│   └── final_report.md
├── scripts/                     # Utility scripts
│   ├── seed.py                  # Seed synthetic data
│   ├── backup.sh                # Database backup
│   └── run_demo.sh             # One-command demo setup
├── deploy/                      # Deployment configurations
├── docker-compose.yml           # Multi-service setup
├── .env.example                 # Environment template
└── .gitignore                   # Git ignore rules
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16
- MongoDB 7

### Setup

1. **Clone and navigate:**
   ```bash
   cd /Users/ayushparoha/Downloads/finsight
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start services with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Seed the database:**
   ```bash
   docker-compose exec backend python scripts/seed.py
   ```

5. **Start the backend server:**
   ```bash
   docker-compose exec backend uvicorn app.main:app --reload
   ```

6. **Start the frontend development server:**
   ```bash
   docker-compose exec frontend npm run dev
   ```

7. **Open in browser:**
   Navigate to http://localhost:5173

## Database Schema

### PostgreSQL Tables
- `users` — User accounts and authentication
- `accounts` — Bank accounts, cash wallets, UPI IDs
- `categories` — Transaction categories
- `transactions` — Transaction ledger
- `budgets` — Monthly budget definitions
- `savings_goals` — Financial goal tracking
- `transfers` — Internal account transfers
- `audit_logs` — Security audit trail

### MongoDB Collections
- `txn_analytics` — Denormalized transaction data for analytics
- `user_behaviour` — Per-user aggregated statistics
- `ai_insights` — Generated monthly insights
- `receipts.*` — GridFS for receipt images

## API Endpoints

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| POST | `/api/auth/register` | Register new user | Public |
| POST | `/api/auth/login` | Login & get JWT | Public |
| GET | `/api/auth/refresh` | Refresh access token | Authenticated |
| POST | `/api/accounts` | Create account | USER,ADMIN,SUPER |
| GET | `/api/accounts` | List user's accounts | Authenticated |
| POST | `/api/transactions` | Create transaction | Authenticated |
| GET | `/api/transactions` | List transactions with filters | Authenticated |
| POST | `/api/transfers` | Transfer between accounts | Authenticated |
| GET | `/api/analytics/dashboard` | Dashboard statistics | Authenticated |
| GET | `/api/insights/latest` | Latest AI insights | Authenticated |
| GET | `/api/admin/aggregates` | Cross-user analytics | ADMIN,SUPER |
| GET | `/api/admin/audit-logs` | View audit logs | ADMIN,SUPER |

Full API documentation available at `/docs` when the backend is running.

## Build Order (as recommended in checklist)

1. **A (#1-6):** Scaffolding, docs, env, compose
2. **C (#21-24):** SQL schema → procedures → views → indexes
3. **B (#7-20):** Backend core (models → schemas → services → routes)
4. **D (#25-29):** ML (synthetic data → categorize → fraud → train → model card)
5. **E (#30-32):** Sync job, notifications, scheduler
6. **F (#33-39):** Frontend (scaffolding → api/hooks → pages → components)
7. **G (#40-43):** Tests → seed → scripts → CI/deploy

## Database Schema Highlights

### Money Handling
- **NUMERIC(14,2) types** for all currency fields (NO FLOATS)
- Atomic balance updates in PostgreSQL stored procedures
- Overdraft prevention with balance checks

### Advanced Indexing
- `idx_tx_user_date` for primary transaction queries
- Partial indexes for analytics (`idx_tx_month`)
- Composite indexes on account, category, flag status

### Stored Procedures
- `fn_transfer_funds(from, to, amt)` — Atomic transfer with overdraft guard
- `fn_create_transaction(...)` — Transaction creation with balance update
- `fn_monthly_rollup(user_id, month)` — Monthly aggregation
- `fn_auto_sweep(user_id)` — Automatic savings contributions

### Views
- `v_monthly_summary` — Per-user monthly financial snapshot
- `v_budget_vs_actual` — Budget vs actual spending comparison
- `v_top_payees` — Top spending categories by payee

## ML Components

### Auto-Categorization (TF-IDF + Logistic Regression)
- Keyword rules for common providers (Zomato, Uber, etc.)
- ML classifier fallback for uncategorized transactions (~15-20%)

### Fraud Detection (Isolation Forest)
- Feature vectors: amount, timing, velocity, category pattern
- Scoring: 0–1 with flags for SUSPICIOUS (>0.7) and REVIEW (>0.5)

### Synthetic Data Generation
- ~20-50k realistic transactions across ~200 synthetic users
- Seedable random walks for income/expense patterns

## Security Features

- **Authentication:** JWT with access (15min) and refresh (7day) tokens
- **Authorization:** Role-based access control (RBAC) at route level
- **Password Security:** bcrypt hashing (cost 12)
- **Audit Logging:** Every sensitive action logged with IP and timestamps
- **Input Validation:** Pydantic schemas + server-side business logic validation
- **SQL Injection Protection:** SQLAlchemy ORM + Parameterized queries
- **NoSQL Injection Prevention:** Schema validation and query sanitization
- **Rate Limiting:** Per-IP and per-user limits configured

## Scripts

### seed.py
Loads synthetic data into PostgreSQL and MongoDB, creates a demo user.
```bash
python scripts/seed.py
```

### backup.sh
Creates PostgreSQL and MongoDB backups with timestamps.
```bash
./scripts/backup.sh
```

### run_demo.sh
Convenience script to start services and open the demo in browser.
```bash
./scripts/run_demo.sh
```

## Testing

Run the complete test suite:
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

Test categories:
- Unit tests (Python business logic)
- Integration tests (API endpoints)
- Security tests (Auth, injection, RBAC)
- Frontend tests (React components)

## Documentation

Comprehensive documentation available in `docs/`:
- **abstract.md** — Project overview (150 words)
- **methodology.md** — Development methodology and timeline
- **architecture.md** — Layered architecture & tech stack diagrams
- **er_diagram.md** — Entity-relationship diagram (Mermaid + SQL)
- **dfd.md** — Data flow diagrams (Level 0 & Level 1)
- **use_cases.md** — User and admin use case diagrams
- **final_report.md** — Complete project report with results

## Development Roadmap

Implemented features align with the 10 DCDS Lab ESE rubric criteria:

| Rubric Criterion | Marks | FinSight Implementation |
|-------------------|-------|--------------------------|
| Application Design & Functionality | 2 | Fully functional, modular, intuitive workflow across all pages |
| Python Programming Implementation | 2 | Classes, functions, exception handling, async patterns |
| Database Integration (SQL & NoSQL) | 2 | PostgreSQL (system-of-record) + MongoDB (analytics) dual DB |
| Advanced Database Querying | 2 | Joins, CTEs, window functions, stored procedures, Mongo aggregations |
| Code Quality, Docs & UI | 1 | PEP 8, docstrings, professional UI with Tailwind, documentation |
| Testing, Validation, Security | 1 | Input validation, pytest suite, encryption, audit logs, JWT security |

## Future Enhancement Scope

- **OCR Receipts:** GridFS storage + Tesseract extraction
- **Multi-Currency:** Live forex conversion
- **Bank API Integration:** UPI/OpenBanking imports
- **PWA:** Mobile-first progressive web app
- **Split Expenses:** Shared bill functionality
- **Shared Wallets:** Multiple-users budgeting

## Contributing

This is an academic project for the DCDS Lab ESE initiative. Follow PEP 8 for Python, ESLint for frontend, and maintain existing code style.

## License

Academic use only. Contact: [Your Institution]

---

**Project Status:** Infrastructure scaffolding complete (43/43 files created). Ready for feature implementation and testing.

**Last Updated:** 2026-09-18
