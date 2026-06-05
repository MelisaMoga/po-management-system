# PO Management System

Full-stack web application for automating the Purchase Order lifecycle — from creation through multi-stage approval to invoicing.

## Tech Stack

| Layer    | Technology         | Why                                      |
|----------|--------------------|------------------------------------------|
| Database | PostgreSQL 15      | Relational, ACID-compliant               |
| Backend  | Python + FastAPI   | REST API, automatic Swagger docs         |
| Frontend | Next.js (React)    | Modern React framework                   |
| ORM      | SQLAlchemy         | Python ↔ PostgreSQL bridge               |

## PO Lifecycle

```
CREATE (Draft)
    │
    ▼
amount >= $100? ──NO──► [bypass] ──┐
    │ YES                           │
    ▼                               │
Pending Manager Approval            │
    │ approve                       │
    ▼ ◄────────────────────────────┘
category = "IT Equipment"? ──NO──► [bypass] ──┐
    │ YES                                       │
    ▼                                           │
Pending IT Validation                          │
    │ approve                                   │
    ▼ ◄────────────────────────────────────────┘
Pending Finance Approval
    │ approve
    ▼
Invoiced ✓

At any approval stage: REJECT → Needs Rework → creator edits → resubmit → restart
```

## User Roles

| Role      | Permissions                                           |
|-----------|-------------------------------------------------------|
| `creator` | Create POs, edit when Needs Rework, resubmit          |
| `manager` | Approve/Reject POs in Pending Manager Approval stage  |
| `it_rep`  | Approve/Reject POs in Pending IT Validation stage     |
| `finance` | Approve/Reject POs in Pending Finance Approval stage  |

## Project Structure

```
po-management/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, CORS, router registration
│   │   ├── database.py      # DB connection, session factory
│   │   ├── models.py        # SQLAlchemy models (tables + enums)
│   │   ├── schemas.py       # Pydantic schemas (API validation)
│   │   ├── crud.py          # DB operations
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── users.py     # User endpoints
│   │       └── po.py        # Purchase Order endpoints
│   ├── seed.py              # Test data generator
│   ├── requirements.txt
│   └── .env
├── frontend/                # Next.js app (Day 3)
├── docker-compose.yml
└── README.md
```

## Running Locally

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.11+
- Node.js 20+

### 1. Start PostgreSQL

```bash
docker compose up -d
```

Verify it's running:
```bash
docker compose ps
```

### 2. Set up Python backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Seed the database

```bash
python seed.py
```

### 4. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

API is now running at: http://localhost:8000  
Swagger UI (interactive docs): http://localhost:8000/docs

### 5. Start the frontend (Day 3)

```bash
cd frontend
npm install
npm run dev
```

Frontend at: http://localhost:3000

## API Endpoints

### Users
| Method | URL              | Description        |
|--------|------------------|--------------------|
| GET    | /api/users/      | List all users     |
| GET    | /api/users/{id}  | Get user by ID     |
| POST   | /api/users/      | Create user        |

### Purchase Orders
| Method | URL                      | Description                     |
|--------|--------------------------|---------------------------------|
| GET    | /api/po/                 | List all POs                    |
| GET    | /api/po/{id}             | Get PO details + audit log      |
| POST   | /api/po/                 | Create new PO (status: Draft)   |
| PATCH  | /api/po/{id}             | Edit PO (only when Needs Rework)|
| POST   | /api/po/{id}/submit      | Submit PO for approval (Day 2)  |
| POST   | /api/po/{id}/approve     | Approve PO (Day 2)              |
| POST   | /api/po/{id}/reject      | Reject PO (Day 2)               |
| POST   | /api/po/{id}/resubmit    | Resubmit after rework (Day 2)   |

## Development Notes

- `echo=True` in `database.py` logs every SQL query — useful for learning, disable in production
- `Base.metadata.create_all()` auto-creates tables — replace with Alembic migrations for production
- Role switching in the frontend simulates authentication — Day 3 implementation detail

## What I Would Improve With More Time

- JWT authentication instead of role-switcher simulation
- Alembic database migrations for schema versioning
- Unit tests with pytest for the state machine logic
- Email notifications when a PO needs attention
- Pagination on the PO list endpoint
- Docker Compose profile for the backend service as well
