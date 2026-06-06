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

## API Endpoints

### Users
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/users/ | List all users |
| GET | /api/users/{id} | Get user by ID |
| POST | /api/users/ | Create user |

### Purchase Orders
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/po/ | List all POs |
| GET | /api/po/{id} | Get PO details + audit log |
| POST | /api/po/ | Create new PO (status: Draft) |
| PATCH | /api/po/{id} | Edit PO (only when Needs Rework) |
| POST | /api/po/{id}/submit | Submit PO for approval |
| POST | /api/po/{id}/approve | Approve PO (role-based) |
| POST | /api/po/{id}/reject | Reject PO with reason |
| POST | /api/po/{id}/resubmit | Resubmit after rework |

## Business Rules

- POs with amount **< $100** bypass Manager Approval automatically
- POs with category **IT Equipment** require IT Validation
- Any approver can reject a PO → status becomes **Needs Rework**
- Creator can edit and resubmit → restarts approval from beginning
- Every action is recorded in the **audit log**

## Project Structure

rinf/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── routes/
│   │       ├── users.py
│   │       └── po.py
│   ├── requirements.txt
│   └── .env
├── frontend/
├── docker-compose.yml
└── README.md

## What I Would Improve With More Time

- [ ] JWT authentication instead of role simulation
- [ ] Email notifications when a PO needs attention
- [ ] Pagination on the PO list endpoint
- [ ] Unit tests for the state machine logic
- [ ] Alembic migrations for DB schema versioning