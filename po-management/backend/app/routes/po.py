"""
routes/po.py — Endpoint-urile pentru Purchase Orders (CRUD de bază)

Ziua 1: Creăm, listăm, vedem detalii.
Ziua 2: Adăugăm submit, approve, reject, resubmit (state machine completă).

Structura URL-urilor:
  GET    /api/po/         → lista tuturor PO-urilor
  GET    /api/po/{id}     → detalii PO
  POST   /api/po/         → creare PO nou
  PATCH  /api/po/{id}     → editare PO (doar în starea NEEDS_REWORK)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..models import UserRole, POStatus
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.POListResponse])
def list_pos(db: Session = Depends(get_db)):
    """Returnează toate PO-urile, sortate descrescător după dată."""
    return crud.get_pos(db)


@router.get("/{po_id}", response_model=schemas.POResponse)
def get_po(po_id: int, db: Session = Depends(get_db)):
    """Returnează un PO cu tot istoricul (audit log inclus)."""
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail=f"PO with id={po_id} not found")
    return po


@router.post("/", response_model=schemas.POResponse, status_code=201)
def create_po(po: schemas.POCreate, db: Session = Depends(get_db)):
    """
    Creează un PO nou în starea DRAFT.
    Statusul inițial e întotdeauna DRAFT — userul trebuie să îl 'submit' explicit.
    """
    # Verificăm că userul există
    user = crud.get_user(db, po.created_by)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id={po.created_by} not found")

    # Verificăm că userul are rol de creator
    if user.role != UserRole.CREATOR:
        raise HTTPException(
            status_code=403,
            detail=f"Only users with role 'creator' can create POs. User has role '{user.role}'"
        )

    return crud.create_po(db, po)


@router.patch("/{po_id}", response_model=schemas.POResponse)
def update_po(po_id: int, updates: schemas.POUpdate, user_id: int, db: Session = Depends(get_db)):
    """
    Editează un PO. Permis doar când PO e în starea NEEDS_REWORK și doar de creator.

    user_id: trimis ca query param (ex: PATCH /api/po/1?user_id=1)
    Ziua 3: înlocuim cu autentificare reală.
    """
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail=f"PO with id={po_id} not found")

    if po.status != POStatus.NEEDS_REWORK:
        raise HTTPException(
            status_code=400,
            detail=f"PO can only be edited when status is 'Needs Rework'. Current status: '{po.status}'"
        )

    if po.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the original creator can edit this PO"
        )

    updated_po = crud.update_po(db, po, updates)

    crud.add_audit_log(
        db=db,
        po_id=po_id,
        action="Edited after rework",
        performed_by=user_id,
        note="PO details updated by creator"
    )

    return updated_po
