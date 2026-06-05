"""
routes/users.py — Endpoint-urile pentru managementul userilor

Concepte FastAPI:
- APIRouter: grupează endpoint-uri (similar cu un namespace)
- Depends(get_db): FastAPI injectează automat sesiunea DB la fiecare request
- response_model: FastAPI validează și serializează răspunsul conform schemei
- status_code=201: codul HTTP pentru "Created" (nu 200)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    """Returnează toți userii din sistem."""
    return crud.get_users(db)


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Returnează un user după ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
    return user


@router.post("/", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Creează un user nou."""
    return crud.create_user(db, user)
