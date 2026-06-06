# PO Management System

A full-stack web application for automating the Purchase Order lifecycle — from creation through multi-stage approval to invoicing.

## Tech Stack

- **Database:** PostgreSQL 15 (via Docker)
- **Backend:** Python + FastAPI
- **Frontend:** Next.js (in progress)
- **ORM:** SQLAlchemy

## PO Lifecycle

    CREATE (Draft)
        │
        ▼
    amount >= $100? ──NO──► [bypass] ──┐
        │ YES                          │
        ▼                              │
    Pending Manager Approval           │
        │ approve                      │
        ▼ ◄────────────────────────────┘
    category = "IT Equipment"? ──NO──► [bypass] ──┐
        │ YES                                     │
        ▼                                         │
    Pending IT Validation                         │
        │ approve                                 │
        ▼ ◄───────────────────────────────────────┘
    Pending Finance Approval
        │ approve
        ▼
    Invoiced ✓

    At any approval stage: REJECT → Needs Rework → creator edits → resubmit → restart

## User Roles

| Role | Permissions |
|------|-------------|
| `creator` | Create POs, edit when Needs Rework, resubmit |
| `manager` | Approve/Reject POs in Pending Manager Approval |
| `it_rep` | Approve/Reject POs in Pending IT Validation |
| `finance` | Approve/Reject POs in Pending Finance Approval |

## Running Locally

### Prerequisites
- Docker Desktop
- Python 3.11+

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Set up Python backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
