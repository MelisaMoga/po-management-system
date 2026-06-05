"""
database.py — Configurarea conexiunii la PostgreSQL

Concepte cheie:
- engine: "motorul" care știe cum să vorbească cu PostgreSQL
- SessionLocal: o fabrică de sesiuni (fiecare request HTTP primește propria sesiune)
- Base: clasa de bază din care moștenesc toate modelele (tabelele)
- get_db: dependency injection pentru FastAPI — deschide sesiunea, o dă endpoint-ului, o închide automat
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://po_user:po_password@localhost:5432/po_management"
)

# echo=True afișează în terminal fiecare query SQL generat — util la debug
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Generator folosit ca dependency în FastAPI.
    Pattern-ul 'yield' garantează că sesiunea se închide chiar și dacă apare o eroare.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
