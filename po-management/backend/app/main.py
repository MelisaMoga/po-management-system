"""
main.py — Punctul de intrare al aplicației FastAPI

Ce se întâmplă la pornire:
1. Base.metadata.create_all(): SQLAlchemy compară modelele cu DB-ul și creează tabelele lipsă
2. CORS middleware: permite browserului (Next.js pe port 3000) să facă request-uri la API (port 8000)
3. Include routers: înregistrează endpoint-urile definite în routes/

Rulare:
  uvicorn app.main:app --reload --port 8000

--reload: server-ul se restartează automat la fiecare modificare (ca inotify în Linux embedded)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import po, users

# Importul modelelor e necesar pentru ca SQLAlchemy să le "vadă" înainte de create_all
from . import models  # noqa: F401

# Creează automat tabelele în DB dacă nu există (bun pentru development)
# În producție s-ar folosi Alembic migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PO Management System",
    description="""
    API pentru managementul Purchase Orders.

    ## Workflow
    1. **Creator** creează un PO (status: Draft)
    2. **Creator** îl submit → intră în flux de aprobare
    3. **Manager** aprobă/respinge (bypass dacă suma < $100)
    4. **IT Rep** validează (doar dacă categoria e IT Equipment)
    5. **Finance** face aprobarea finală
    6. PO e marcat ca **Invoiced**

    La orice pas de aprobare, PO poate fi **respins** → status: Needs Rework
    """,
    version="1.0.0",
    docs_url="/docs",       # Swagger UI la http://localhost:8000/docs
    redoc_url="/redoc"      # ReDoc UI la http://localhost:8000/redoc
)

# CORS — permite Next.js (localhost:3000) să apeleze API-ul (localhost:8000)
# Fără asta, browserul blochează request-urile cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Înregistrarea router-elor cu prefix-uri
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(po.router, prefix="/api/po", tags=["Purchase Orders"])


@app.get("/", tags=["Health"])
def root():
    """Health check — verifică că API-ul rulează."""
    return {
        "status": "ok",
        "message": "PO Management API is running",
        "docs": "http://localhost:8000/docs"
    }
