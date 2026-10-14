# Feedback Intelligence System

An AI-powered platform that collects customer feedback from multiple touchpoints, normalizes and cleans text, classifies sentiment and operational categories, detects emerging trends and spikes in dissatisfaction, and delivers actionable business insights through an executive React dashboard.

---

## 1. Project Overview

Modern businesses receive customer feedback across numerous disparate channels: web forms, support tickets, app store reviews, emails, and social media. Processing this feedback manually leads to delays in addressing operational failures, churn risks, and missed feature opportunities.

The **Feedback Intelligence System** automates this pipeline end-to-end:
1. **Multi-Channel Ingestion:** Standardized ingestion of raw feedback with customer identifiers, source metadata, and validation.
2. **Text Processing & ML Intelligence:** Cleans text, applies sentiment analysis with confidence scoring, and categorizes input across key business areas (Product Quality, Customer Support, Pricing, Delivery, User Experience, Feature Requests).
3. **Trend Detection:** Detects temporal velocity, analyzes sentiment ratios over time, and triggers alerts on statistically meaningful spikes in negative feedback.
4. **Actionable Recommendations:** Generates executive summaries and targeted recommendations (with optional OpenAI enhancement while functioning fully offline with baseline heuristic ML).
5. **Interactive Executive Dashboard:** Fast, responsive React dashboard powered by Tailwind CSS, Chart.js, and real-time backend health monitoring.

---

## 2. Technology Stack

- **Backend:**
  - Python 3.11+
  - FastAPI (REST API with versioning, OpenAPI / Swagger documentation)
  - Pydantic v2 & `pydantic-settings`
  - SQLAlchemy 2.x (ORM with connection pooling and pre-ping)
  - PostgreSQL (Production database) & SQLite (Local fallback / test runner)
  - Alembic (Database schema migrations)
  - Redis & Celery (Asynchronous task queues and batch processing)
  - scikit-learn & NumPy (Baseline ML classification & statistical trend analysis)
  - Optional OpenAI API integration (Executive summaries)

- **Frontend:**
  - React 18 & Vite
  - Tailwind CSS
  - React Router v6
  - Axios (HTTP client with response error interception)
  - Chart.js & react-chartjs-2 (Data visualization)
  - Lucide React (Icons)

- **Testing & Quality Assurance:**
  - Pytest & HTTPX (Backend route, model, and intelligence tests)
  - Vitest & React Testing Library (Frontend unit & component tests)

- **DevOps & Containerization:**
  - Docker & multi-stage Dockerfiles
  - Docker Compose (FastAPI, React, PostgreSQL, Redis, Celery worker)
  - GitHub Actions CI/CD pipeline

---

## 3. Architecture & Repository Structure

### 3.1 Dedicated Technical Documentation
- **[System Architecture & Design Document](docs/ARCHITECTURE.md)**: Component design, data flow diagrams, database schemas, and security boundaries.
- **[REST API Reference & Endpoints](docs/API.md)**: Complete endpoint contracts, query parameters, request schemas, and sample JSON payloads.
- **[Testing & Quality Assurance Guide](docs/TESTING.md)**: Test pyramid, execution commands, coverage breakdown (77 backend + 16 frontend), and edge case verifications.
- **[Production Deployment & Operations Guide](docs/DEPLOYMENT.md)**: VPS setup, Docker Compose override, backup/restore runbooks, and SSL configuration.

### 3.2 High-Level Architecture Diagram
```mermaid
flowchart TD
    subgraph Client Tier
        Browser["Web Browser Client"]
        SPA["React 18 + Vite SPA<br/>(Tailwind CSS, Lucide, Recharts)"]
    end

    subgraph Edge & Ingress Tier
        Nginx["Nginx Reverse Proxy<br/>(Port 80/443, SPA fallback)"]
    end

    subgraph Application Tier
        FastAPI["FastAPI 0.115 Backend<br/>(Uvicorn ASGI Engine)"]
        AuthModule["Security & Auth Middleware<br/>(JWT, BCrypt, RBAC, RateLimiter)"]
        NLPEngine["Local NLP Engine<br/>(TextCleaner, VADER, RuleCategorizer)"]
        CeleryWorker["Celery 5.4 Worker<br/>(Async Bulk NLP Tasks)"]
    end

    subgraph Data & Message Tier
        Postgres[(PostgreSQL 16 Database<br/>Indexed Relational Store)]
        Redis[(Redis 7 In-Memory Broker<br/>Celery Queue & Token Denylist)]
    end

    Browser -->|HTTPS / HTTP| Nginx
    Nginx -->|Static Assets / Index SPA| SPA
    Nginx -->|/api/* & /health & /ready Reverse Proxy| FastAPI
    SPA -->|REST API Requests with Bearer JWT| FastAPI

    FastAPI --> AuthModule
    AuthModule -->|Validate Token / Denylist| Redis
    FastAPI -->|Synchronous Analysis| NLPEngine
    FastAPI -->|Enqueue Heavy Background Jobs| Redis
    Redis -->|Consume Task Queues| CeleryWorker
    CeleryWorker -->|Process Analytics| NLPEngine
    CeleryWorker -->|Update Feedback Records| Postgres
    FastAPI -->|SQLAlchemy 2.0 ORM| Postgres
```

### 3.3 Directory Structure
```
feedback-intelligence-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # Application entrypoint & middleware
│   │   ├── api/                 # API routing
│   │   │   └── v1/
│   │   │       ├── api.py       # API v1 router aggregator
│   │   │       ├── health.py    # Health & readiness endpoints
│   │   │       ├── feedback.py  # Feedback CRUD & analysis routes
│   │   │       └── analytics.py # Sentiment, category, trend analytics
│   │   ├── core/                # App config, logging, centralized errors
│   │   ├── db/                  # SQLAlchemy base, sessions, seeding
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Core business logic layer
│   │   ├── ingestion/           # Data normalization & source adapters
│   │   ├── processing/          # Text cleaning & preprocessing
│   │   ├── intelligence/        # Sentiment analysis, categorization, trends
│   │   ├── tasks/               # Celery app & async worker tasks
│   │   └── integrations/        # Optional OpenAI & external API clients
│   ├── tests/                   # Pytest test suite
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend container definition
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI (Badges, Spinner, Empty state)
│   │   ├── pages/               # Overview, Feed, Details, Form, Analytics
│   │   ├── layouts/             # DashboardLayout with sidebar & health pill
│   │   ├── services/            # Axios API clients
│   │   ├── hooks/               # Custom React hooks
│   │   └── utils/               # Formatting & helper utilities
│   ├── package.json             # Frontend dependencies & scripts
│   ├── vite.config.js           # Vite dev server & test config
│   └── Dockerfile               # Frontend container definition
├── docs/                        # Architecture diagrams & specifications
├── deployment/                  # Production deployment artifacts
├── docker-compose.yml           # Multi-service composition
├── .env.example                 # Environment variables template
├── .gitignore                   # Version control exclusions
└── README.md                    # Project documentation
```

---

## 4. Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- (Optional for containerized mode) Docker and Docker Compose
- (Optional for full production services) PostgreSQL 15+ and Redis 7+

---

## 5. Local Installation & Quick Start

### 5.1 Clone & Environment Setup

```bash
# Navigate to the project root
cd feedback-intelligence-system

# Copy environment template
cp .env.example .env
```

Review `.env` and adjust database credentials or ports if desired. The system defaults to local SQLite if PostgreSQL is not running.

---

### 5.2 Backend Setup

```bash
cd backend

# Create and activate virtual environment (Windows PowerShell)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# (On Linux / macOS):
# python3.11 -m venv .venv
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# --- PostgreSQL Setup (Production / Local PostgreSQL) ---
# 1. Create database in PostgreSQL:
#    createdb -U postgres feedback_db
#    (or in psql: CREATE DATABASE feedback_db;)
#
# 2. Update .env with your credentials:
#    DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/feedback_db
#
# 3. Apply Alembic migrations:
alembic upgrade head

# (Optional: Generate a new migration schema after model modifications)
# alembic revision --autogenerate -m "describe changes"

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive OpenAPI documentation is now accessible at:
- Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

---

### 5.3 Background Worker Setup (Celery & Redis)

For asynchronous NLP analysis and background batch processing:

1. **Start Redis server:**
   ```bash
   # Using local Redis or Docker:
   docker run -d --name local-redis -p 6379:6379 redis:7-alpine
   ```

2. **Start Celery worker:**
   ```bash
   cd backend
   # Linux / macOS:
   celery -A app.tasks.celery_app.celery_app worker --loglevel=info

   # Windows (PowerShell):
   celery -A app.tasks.celery_app.celery_app worker --loglevel=info -P solo
   ```

---

### 5.4 Frontend Setup

```bash
cd ../frontend

# Copy environment template
cp .env.example .env

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to access the dashboard.
Configure `VITE_API_BASE_URL` in `frontend/.env` if your backend runs on a custom port or domain (defaults to `http://localhost:8000/api/v1`).

---

## 6. Running with Docker Compose

To spin up all 5 services (PostgreSQL, Redis, Celery Worker, FastAPI backend, and React frontend) with a single command:

```bash
# Build and start all services in detached mode
docker compose up --build -d

# View container logs
docker compose logs -f

# Stop all containers
docker compose down

# Stop and delete volumes (resets database)
docker compose down -v
```

Services exposed:
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000) (Nginx SPA)
- **Backend API & Docs:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **PostgreSQL Database:** `localhost:5432` (persistent volume `postgres_data`)
- **Redis Queue:** `localhost:6379`
- **Celery Worker:** Running in background with concurrency 2 and auto-retry

---

## 7. API Documentation

| Method | Endpoint | Required Role | Description |
|---|---|---|---|
| `GET` | `/health` | Public | Liveness probe returning server status and timestamp |
| `GET` | `/ready` | Public | Readiness probe verifying database connectivity |
| `POST` | `/api/v1/auth/register` | Public | Register new user account (role: `viewer` or `analyst`) |
| `POST` | `/api/v1/auth/login` | Public | Authenticate user credentials and receive JWT access token |
| `GET` | `/api/v1/auth/me` | Authenticated | Retrieve current user profile and role |
| `POST` | `/api/v1/auth/logout` | Authenticated | Invalidate client session token |
| `GET` | `/api/v1/users` | Admin | Paginated list of registered users |
| `GET` | `/api/v1/users/{id}` | Admin | Get details of specific user |
| `PATCH` | `/api/v1/users/{id}` | Admin | Update user profile details |
| `PATCH` | `/api/v1/users/{id}/role` | Admin | Change user role (`admin`, `analyst`, `viewer`) |
| `PATCH` | `/api/v1/users/{id}/status` | Admin | Activate or deactivate user account |
| `DELETE` | `/api/v1/users/{id}` | Admin | Delete user account (safeguarded against last admin) |
| `POST` | `/api/v1/feedback` | Analyst, Admin | Ingest and validate a new customer feedback item |
| `GET` | `/api/v1/feedback` | Authenticated | Paginated list of feedback with search and filters |
| `GET` | `/api/v1/feedback/{id}` | Authenticated | Retrieve details of a specific feedback record |
| `PATCH` | `/api/v1/feedback/{id}` | Analyst, Admin | Update status or fields of a feedback record |
| `DELETE` | `/api/v1/feedback/{id}` | Admin | Permanently delete a feedback record |
| `POST` | `/api/v1/feedback/{id}/analyze` | Analyst, Admin | Synchronously analyze sentiment and category |
| `POST` | `/api/v1/feedback/{id}/analyze-async` | Analyst, Admin | Asynchronously enqueue Celery analysis task (HTTP 202) |
| `POST` | `/api/v1/feedback/batch-analyze` | Analyst, Admin | Synchronously batch analyze pending items |
| `POST` | `/api/v1/feedback/batch-analyze-async` | Analyst, Admin | Asynchronously enqueue batch analysis task (HTTP 202) |
| `GET` | `/api/v1/tasks/{task_id}` | Authenticated | Inspect background task status, execution state, and output |
| `GET` | `/api/v1/analytics/overview` | Authenticated | High-level metrics (total feedback, sentiment totals) |
| `GET` | `/api/v1/analytics/sentiment` | Authenticated | Detailed sentiment distribution breakdown |
| `GET` | `/api/v1/analytics/categories` | Authenticated | Count of feedback grouped by business category |
| `GET` | `/api/v1/analytics/trends` | Authenticated | Time-series data points, negative spike alerts, and summaries |

### 7.1 Async Task Status Example

#### `GET /api/v1/tasks/a9ef33d3-3fc1-4be1-bd10-ac89b2acde51`
```json
{
  "task_id": "a9ef33d3-3fc1-4be1-bd10-ac89b2acde51",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "result": {
    "task_id": "a9ef33d3-3fc1-4be1-bd10-ac89b2acde51",
    "feedback_id": 17,
    "status": "completed",
    "sentiment": "positive",
    "sentiment_score": 0.92,
    "category": "Customer Support"
  },
  "error": null
}
```

### 7.2 Analytics API Response Examples

#### `GET /api/v1/analytics/overview`
```json
{
  "total_feedback": 128,
  "positive_count": 72,
  "negative_count": 34,
  "neutral_count": 22,
  "analyzed_count": 120,
  "pending_count": 8,
  "sentiment_distribution": {
    "positive": 56.3,
    "neutral": 17.2,
    "negative": 26.6
  }
}
```

---

## 8. Security, Authentication & Role-Based Access Control (RBAC)

### 8.1 Role Permission Matrix

| Capability | Admin | Analyst | Viewer |
|---|:---:|:---:|:---:|
| View Feedback & Details | Yes | Yes | Yes |
| View Analytics, Trends & Summaries | Yes | Yes | Yes |
| Ingest New Feedback | Yes | Yes | No |
| Update Feedback & Status | Yes | Yes | No |
| Run Sentiment & Category Analysis | Yes | Yes | No |
| Batch Process Unanalyzed Feedback | Yes | Yes | No |
| Delete Feedback Records | Yes | No | No |
| Access User Management Directory | Yes | No | No |
| Modify User Roles & Account Status | Yes | No | No |

### 8.2 Authentication Flow & Password Hashing
- **Password Security:** Salted hashes generated using `bcrypt` (12 rounds) with non-deterministic salting. Plaintext passwords are never logged or stored.
- **Stateless JWT Tokens:** Standard RFC 7519 JWT signed with HMAC-SHA256 (`HS256`). Tokens carry `sub` (user id), `role`, `name`, `iat`, and `exp` claims.
- **Anti-Enumeration Login:** Login attempts for non-existent emails return identical `401 Unauthorized ("Incorrect email or password.")` responses to mitigate user enumeration attacks.
- **Initial Administrator Setup:**
  Provide `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` in `.env`. On startup, the system seeds the initial administrator account automatically if none exists.
  ```bash
  # Windows PowerShell example:
  $env:INITIAL_ADMIN_EMAIL="admin@company.com"
  $env:INITIAL_ADMIN_PASSWORD="SecureAdminPassword2026!"
  ```
- **Last Administrator Protection:** The system strictly prevents demoting, deactivating, or deleting the last active administrator account, eliminating lockout risks.

### 8.3 Rate Limiting & Protection
- In-memory sliding-window rate limiter returns `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` headers.
- Exceeding limits returns `HTTP 429 Too Many Requests`.
- Authentication endpoints (`/api/v1/auth/login`, `/register`) are throttled at 15 requests per minute to prevent brute-force attacks.

### 8.4 Security Headers
All HTTP responses include hardened security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` (clickjacking defense)
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (enforced in production)

---

## 9. AI/ML Intelligence Architecture


The intelligence pipeline runs entirely locally by default without requiring external cloud models, internet access, or paid API keys.

### 8.1 Text Preprocessing Pipeline (`app/processing/cleaner.py`)
- **Validation:** Strict character bounds and rejection of empty or non-string values.
- **Unicode Normalization:** NFKC normalization, converting typographic quotes (`“`, `”`, `’`), dashes (`—`, `–`), and non-breaking spaces.
- **Whitespace Collapsing:** Replaces multi-space, tabs, and carriage returns with clean single spaces.
- **Context & Negation Preservation:** Crucially preserves punctuation (`!`, `?`) and negation tokens (`not`, `never`, `no`, `cannot`, `don't`) which invert downstream sentiment.

### 8.2 Sentiment Analysis (`app/intelligence/sentiment_analyzer.py`)
- **Baseline Approach:** Transparent lexical valence scoring using curated sentiment dictionaries (-3.0 to +3.0).
- **Negation Window:** Lookbehind window of 3 tokens. Odd counts of negations within the window invert and slightly dampen the target word valence.
- **Intensifier Scaling:** Multipliers for adverbs (e.g. *extremely*, *super*, *really* vs *slightly*).
- **Hyperbolic Polarity Normalization:**
  $$\text{compound} = \frac{\sum w}{\sqrt{(\sum w)^2 + 15.0}} \in [-1.0, +1.0]$$
- **Confidence Calibration:** Scores are bounded between `0.50` and `0.99`, reflecting evidence density and signal magnitude rather than arbitrary numbers.
- **Model Replaceability:** Governed by `BaseSentimentAnalyzer`, allowing seamless drop-in replacement with Hugging Face transformers or fine-tuned scikit-learn models without altering the REST API contract.

### 8.3 Categorization Engine (`app/intelligence/categorizer.py`)
- **Supported Categories:**
  1. `Product Quality`
  2. `Customer Support`
  3. `Pricing`
  4. `Delivery`
  5. `User Experience`
  6. `Feature Request`
  7. `Other` (Fallback)
- **Baseline Approach:** Multi-word phrase cues (weight 2.5) and single keyword tokens (weight 1.0) with normalized confidence scoring.
- **Fallback Rule:** If best category confidence is below `CLASSIFICATION_THRESHOLD` (default 0.30) or total evidence is negligible, the system safely assigns `Other`.

### 8.4 Known Limitations of the Baseline
- **Sarcasm / Irony:** Lexicon-based baseline analyzers cannot detect nuanced sarcasm (e.g. *"Oh fantastic, my order was lost again"*).
- **Compound Domain Feedback:** When a review spans multiple operational areas equally, the dominant category is chosen based on cue frequency.
- **Out-of-Vocabulary Terms:** Slang or domain acronyms not in the dictionary default to neutral score.

---

## 10. Comprehensive Testing & Quality Assurance (Phase 8)

The system features an automated test pyramid spanning database migrations, data constraints, text processing, AI/ML intelligence, background processing, security headers, RBAC authentication, and React dashboard interactions.

### 10.1 Testing Prerequisites & Environment Setup

- **Python:** 3.11+ with active virtual environment (`.venv`).
- **Node.js:** 20+ with npm dependencies installed.
- **Test Database:** Automatically configured as an isolated, in-memory/file-based SQLite database (`DATABASE_URL=sqlite:///./test_feedback.db`, `ENVIRONMENT=testing`) during pytest runs. No live PostgreSQL or Redis instance is required to execute tests.

### 10.2 Backend Test Suite (Pytest — 77 Tests)

The backend test suite contains **77 automated tests** across 13 dedicated test modules:

| Test Module | Coverage Scope | Tests |
|---|---|:---:|
| `tests/test_analysis_api.py` | Synchronous feedback analysis and batch analyze endpoints | 4 |
| `tests/test_analytics.py` | Overview, sentiment distribution, categories, and trends | 4 |
| `tests/test_auth.py` | User registration, login, JWT validation, expiration, and logout | 11 |
| `tests/test_categorizer.py` | Operational classification rules across 7 business categories | 7 |
| `tests/test_cleaner.py` | Unicode NFKC normalization, whitespace collapsing, tokenization | 7 |
| `tests/test_database_integrity.py` | DB CheckConstraints, unique emails, transaction rollbacks, sorting | 6 |
| `tests/test_feedback.py` | Full Feedback CRUD lifecycle, pagination, and input validation | 9 |
| `tests/test_health.py` | Liveness, readiness, and root probe status endpoints | 4 |
| `tests/test_migrations.py` | Isolated Alembic migration lifecycle (`upgrade head` & `downgrade base`) | 1 |
| `tests/test_qa_edge_cases.py` | Boundary lengths (10,000 chars), emojis, phrase precedence, task polling | 6 |
| `tests/test_security.py` | RBAC role guards (`viewer`, `analyst`, `admin`), rate limits, headers | 6 |
| `tests/test_sentiment.py` | Lexicon scoring, negation inversion windows, compound score bounds | 6 |
| `tests/test_tasks.py` | Celery async worker tasks, duplicate prevention, and async endpoints | 6 |
| **Total Passed** | **Zero failures, zero deprecation warnings** | **77** |

#### Run Backend Tests (Windows PowerShell)

```powershell
# Navigate to backend directory
cd backend

# Run the complete test suite (77 tests)
.\.venv\Scripts\pytest.exe -v

# Run specific functional areas
.\.venv\Scripts\pytest.exe tests/test_database_integrity.py tests/test_migrations.py -v
.\.venv\Scripts\pytest.exe tests/test_auth.py tests/test_security.py -v
.\.venv\Scripts\pytest.exe tests/test_tasks.py tests/test_qa_edge_cases.py -v
```

### 10.3 Database Migration Testing (Alembic)

Verify database migration consistency and head revision status:

```powershell
cd backend

# Inspect current migration heads
.\.venv\Scripts\alembic.exe heads

# Apply all migrations to the latest revision
.\.venv\Scripts\alembic.exe upgrade head

# Roll back the most recent migration (if needed)
.\.venv\Scripts\alembic.exe downgrade -1
```

### 10.4 Frontend Test Suite (Vitest — 16 Tests)

The frontend test suite verifies metric card calculations, chart rendering, filter inputs, feedback forms, and Phase 7 authentication / protected routes:

| Test File | Component Scope | Tests |
|---|---|:---:|
| `src/Auth.test.jsx` | Login form submission, session persistence, role-aware routing | 4 |
| `src/Dashboard.test.jsx` | Live metric cards, data loading states, error boundaries | 3 |
| `src/App.test.jsx` | FeedbackForm validation, navigation, status badge rendering | 9 |
| **Total Passed** | **Zero failures** | **16** |

#### Run Frontend Tests & Production Build

```powershell
# Navigate to frontend directory
cd frontend

# Run frontend test suite
npm test -- --run

# Run production build (verifies Vite bundling of 1590+ modules)
npm run build
```

### 10.5 Docker Compose Validation

Validate multi-container schema, service definitions, environment bindings, and network topologies without starting daemon containers:

```powershell
# From repository root
docker compose config
```

### 10.6 Known Limitations & Test Isolation Strategy

1. **Celery Worker Execution in Tests:** During automated testing (`ENVIRONMENT=testing`), Celery runs in eager in-memory mode (`task_always_eager=True`). End-to-end multi-container distributed worker validation with live Redis is executed via `docker compose up`.
2. **Database Engine in Local Test Runner:** Pytest runs against SQLite with SQLAlchemy abstract types to allow isolated fast test runs without requiring local PostgreSQL services. Schema compatibility is verified via Alembic migrations.
3. **Stateless JWT Revocation:** Server-side token invalidation on `/auth/logout` maintains an in-memory denylist that automatically synchronizes with Redis when `REDIS_URL` is configured in production.

---

## 11. CI/CD Pipeline (GitHub Actions)

Continuous Integration is configured via `.github/workflows/ci.yml` running on all pushes and pull requests against `main` and `master`:

1. **Backend Job (`backend-tests`):**
   - Sets up Python 3.11 with pip dependency caching.
   - Installs dependencies from `backend/requirements.txt`.
   - Executes Pytest test suite with isolated SQLite database and test JWT secret.
2. **Frontend Job (`frontend-tests`):**
   - Sets up Node.js 20 with npm package caching.
   - Installs dependencies cleanly via `npm ci`.
   - Executes Vitest test suite and builds production static bundle via `npm run build`.
3. **Docker Validation Job (`docker-validation`):**
   - Validates `docker-compose.yml` configuration syntax.
   - Builds backend and frontend Docker images to prevent container regression.

---

## 12. Production Deployment & Hosting Guide (Phase 9)

### 12.1 Recommended Hosting Architecture

For student portfolios, demonstrations, and production deployments, the system is designed to run either as a unified containerized stack or as modular cloud services:

```
[ Internet User / Browser ]
           │
           ▼
[ Reverse Proxy / TLS Termination (Nginx :443) ]
     │                                    │
     ▼                                    ▼
[ React Frontend (Nginx SPA :80) ]   [ FastAPI Backend (Uvicorn ASGI :8000) ]
                                          │             │
                    ┌─────────────────────┘             └──────────────────┐
                    ▼                                                      ▼
     [ PostgreSQL 16 (DB:5432) ]                                  [ Redis 7 (:6379) ]
                    ▲                                                      │
                    └────────────── [ Celery Worker ] ─────────────────────┘
```

#### Hosting Strategy Comparison

| Provider / Model | Monthly Cost | PostgreSQL | Redis | Celery Worker | Best For |
|---|:---:|:---:|:---:|:---:|---|
| **Option A: Linux VPS + Docker Compose** *(Hetzner / DigitalOcean / AWS Lightsail)* | **$3.50 – $6/mo** | Included (Container) | Included (Container) | Included (Container) | **Recommended:** Complete 1:1 parity with dev, persistent workers, zero idle spin-down. |
| **Option B: PaaS (Render)** | Free to $14/mo | Managed Free (30 days) | Managed Free (30 days) | Paid background worker ($7/mo) | Simple Git-push setup; requires paid tier for 24/7 worker uptime. |
| **Option C: PaaS (Railway)** | $5 trial, then usage-based | Managed Plugin | Managed Plugin | Included in unified project | Quickest cloud deployment; automatically builds Dockerfiles. |
| **Option D: Hybrid Managed** *(Vercel + Cloud Run + Supabase + Upstash)* | Free tier eligible | Free Supabase (500MB) | Free Upstash (10k cmds/day) | Cloud Run Job or low-tier container | Serverless architecture; requires multiple account configurations. |

---

### 12.2 Deployment Option A: Unified Docker Compose (Recommended)

This strategy deploys all 5 containers on a virtual private server (Ubuntu 22.04 / 24.04 LTS):

#### Step 1: Server Provisioning & Docker Installation
```bash
# Connect to your server
ssh user@your-server-ip

# Install Docker & Docker Compose plugin
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### Step 2: Clone Repository & Configure Production Environment
```bash
cd /opt
sudo git clone https://github.com/your-username/feedback-intelligence-system.git
cd feedback-intelligence-system

# Create secure production environment file from template
sudo cp .env.example .env

# Generate a cryptographically secure 64-character SECRET_KEY
openssl rand -hex 32
```

Edit `/opt/feedback-intelligence-system/.env` with production values:
```bash
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<output_from_openssl_rand>
POSTGRES_PASSWORD=<strong_random_db_password>
INITIAL_ADMIN_EMAIL=admin@yourdomain.com
INITIAL_ADMIN_PASSWORD=<strong_admin_password>
BACKEND_CORS_ORIGINS=["https://feedback.yourdomain.com"]
VITE_API_BASE_URL=""
```

#### Step 3: Launch Containers with Production Hardening
```bash
# Launch containers with production overrides (closed DB ports, log rotation, resource limits)
sudo docker compose -f docker-compose.yml -f deployment/docker-compose.prod.yml up -d --build

# Verify container status
sudo docker compose ps

# Inspect backend startup and automatic migration execution
sudo docker compose logs backend
```

#### Step 4: Configure Host Nginx & Free SSL (Let's Encrypt / Certbot)
```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Copy production Nginx reverse proxy template
sudo cp deployment/nginx.prod.conf /etc/nginx/sites-available/feedback
sudo sed -i 's/feedback.yourdomain.com/your-domain.com/g' /etc/nginx/sites-available/feedback
sudo ln -s /etc/nginx/sites-available/feedback /etc/nginx/sites-enabled/
sudo nginx -t

# Obtain SSL Certificate
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

---

### 12.3 Database Migrations & Backup Strategy

#### Running Migrations in Production
Alembic migrations run automatically on container startup via the entrypoint in `docker-compose.yml`. To execute migrations manually:
```bash
# Execute migrations to latest revision
sudo docker compose exec backend alembic upgrade head

# Inspect current revision status
sudo docker compose exec backend alembic current
```

#### Database Backup & Recovery Procedures
```bash
# Create an immediate compressed database backup
sudo docker compose exec postgres pg_dump -U postgres feedback_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore database from a backup
gunzip < backup_20261014_120000.sql.gz | sudo docker compose exec -T postgres psql -U postgres -d feedback_db
```

---

### 12.4 Background Worker Monitoring (Celery + Redis)

Monitor Celery task queues and worker liveness:
```bash
# Ping worker to verify responsiveness
sudo docker compose exec celery_worker celery -A app.tasks.celery_app.celery_app inspect ping

# Inspect active running tasks
sudo docker compose exec celery_worker celery -A app.tasks.celery_app.celery_app inspect active

# Check Redis queue length
sudo docker compose exec redis redis-cli llen celery
```

---

## 13. Post-Deployment Verification Checklist

Execute these 15 verification steps immediately following production deployment:

- [ ] **1. Frontend Loading:** Navigate to `https://your-domain.com` and verify the React application loads without console errors.
- [ ] **2. Backend Liveness Probe:** `curl -f https://your-domain.com/health` returns HTTP 200 with `status: "ok"`.
- [ ] **3. Backend Readiness Probe:** `curl -f https://your-domain.com/ready` returns HTTP 200 with `database: "healthy"` and `redis: "healthy"`.
- [ ] **4. API Documentation:** Navigate to `https://your-domain.com/api/v1/docs` and confirm OpenAPI documentation renders.
- [ ] **5. Database Connectivity:** Verify database connectivity pill displays "API Connected" in the dashboard sidebar.
- [ ] **6. Schema Integrity:** Confirm Alembic migration head `918ce4082049` is applied.
- [ ] **7. Initial Admin Login:** Log in via `/login` using `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD`.
- [ ] **8. Role-Based Permissions:** Confirm Viewer accounts cannot access `/submit` or `/users` (redirects to `/unauthorized`).
- [ ] **9. Feedback Ingestion:** Ingest a test customer review via `/submit` and confirm it appears in `/feedback`.
- [ ] **10. Sentiment & Category ML:** Run synchronous analysis on a feedback item and verify sentiment classification and category assignment.
- [ ] **11. Celery Async Task Execution:** Trigger asynchronous batch analysis and poll `/api/v1/tasks/{task_id}` until `status: "SUCCESS"`.
- [ ] **12. Real-Time Analytics:** Verify `/analytics` charts update dynamically reflecting actual database feedback volume.
- [ ] **13. Negative Spike Detection:** Verify trend charts correctly compute daily data points and render spike banners if criteria are met.
- [ ] **14. Security Headers:** Inspect response headers in browser dev tools for `X-Content-Type-Options: nosniff` and `Strict-Transport-Security`.
- [ ] **15. Client Refresh Persistence:** Refresh any client page (e.g. `/analytics`, `/feedback/1`) and verify Nginx SPA routing serves `index.html` without 404 errors.

---

## 14. Troubleshooting & Production Runbook

- **502 Bad Gateway on Frontend:**
  The backend container is initializing or running database migrations. Inspect backend logs: `docker compose logs -f backend`.
- **Database Connection Refused:**
  Ensure the `postgres` container passes healthcheck (`docker compose ps`). The backend waits for the database to be healthy before starting.
- **CORS Rejected on Browser:**
  Ensure the exact protocol and domain (e.g. `https://your-domain.com`) are present in `BACKEND_CORS_ORIGINS` inside `.env`.
- **Worker Missing Tasks:**
  Verify Redis is healthy (`docker compose exec redis redis-cli ping`). Inspect Celery worker logs: `docker compose logs -f celery_worker`.
- **Token Invalidation / Revocation:**
  When a user logs out, their JWT is placed on a denylist. If Redis is configured, the denylist syncs across all workers; in local development, it maintains an in-memory set.
- **Log Sanitation:**
  All application logs are sanitized automatically via `app/core/logging.py`, redacting sensitive credentials and access tokens to `[REDACTED]`.

---

## 15. Known Limitations & Future Roadmap

### Current Architectural Limitations
1. **Language Scope:** The offline NLP preprocessing and sentiment analyzer are calibrated primarily for English text. Accents and Romanized text are normalized, but non-English verbatims require multi-lingual transformer integration.
2. **Aspect-Based Parsing (ABSA):** When a single feedback contains contrasting thoughts (*"Great product quality, but horrible delivery delay"*), the compound score reflects the net valence rather than distinct aspect breakdown.
3. **Lexical Sarcasm Detection:** Sophisticated rhetorical sarcasm (*"Oh fantastic, my package was stolen again"*) is scored positively by dictionary valences.
4. **WebSocket Push Notifications:** Background Celery tasks update the database; currently, frontend clients poll `/api/v1/tasks/{task_id}` rather than receiving real-time WebSocket push events.

### Planned Enhancements
- **Multi-Lingual Transformer Models:** Optional plug-and-play ONNX Runtime wrapper for lightweight multilingual DistilBERT.
- **Aspect-Based Sentiment Extraction:** Token dependency parsing to isolate and score separate business features independently.
- **Bulk CSV / Excel Ingestion Wizard:** Drag-and-drop CSV importer in the frontend with automatic column mapping.
- **Slack & PagerDuty Webhooks:** Automated threshold alerts dispatched to DevOps/Support channels when a negative spike occurs.

---

## 16. Project Presentation & Demonstration Walkthrough

Follow this 5-minute walkthrough during portfolio reviews, interviews, or presentation demos:

### Step 1: Authentication & RBAC Demonstration
1. Open the application at `http://localhost:3000` (or `http://localhost:5173` in local dev).
2. Register an account with role **Analyst** or log in as **Admin**.
3. Point out role-based navigation: Analysts can access **Submit Feedback**, whereas **User Management** is strictly reserved for Admins.

### Step 2: Executive Dashboard Overview
1. Observe the live KPI cards: Total Feedback Ingested, Positive/Negative/Neutral counts, and Analyzed Percentage.
2. Verify that metrics update from real PostgreSQL data rather than static mock fixtures.
3. Observe the bottom status indicator showing real-time API and database connectivity (`API Status: online`, `DB: connected`).

### Step 3: Feedback Ingestion & NLP Intelligence
1. Navigate to **Submit Feedback** (`/submit`).
2. Enter sample text: *"The checkout process was incredibly fast and customer support helped me in 2 minutes! Super impressed."*
3. Check **Run AI analysis immediately** and click **Submit Feedback**.
4. The system automatically redirects to the feedback detail page, displaying:
   - **Sentiment:** `positive` with confidence score ~0.85–0.95.
   - **Operational Category:** `Customer Support` (or `User Experience`).

### Step 4: Analytics, Trends & Spike Alerts
1. Navigate to **Analytics & Trends** (`/analytics`).
2. Inspect the **Sentiment Distribution** breakdown and **Operational Category** bar chart.
3. Inspect the **Feedback Volume & Sentiment Trends** time-series graph.
4. Highlight the **AI Summary & Actionable Recommendations** box synthesized dynamically from current feedback distributions.

### Step 5: Security & Session Invalidation
1. Click **Sign Out** in the navigation sidebar.
2. The client clears the token and redirects to `/login`.
3. Highlight that the backend token denylist immediately invalidates the JWT so it cannot be replayed.

---

## 17. License

Distributed under the **MIT License**. See `LICENSE` for more information.


