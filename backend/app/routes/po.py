from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..models import UserRole, POStatus
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.POListResponse])
def list_pos(db: Session = Depends(get_db)):
    return crud.get_pos(db)


@router.get("/{po_id}", response_model=schemas.POResponse)
def get_po(po_id: int, db: Session = Depends(get_db)):
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    return po


@router.post("/", response_model=schemas.POResponse, status_code=201)
def create_po(po: schemas.POCreate, db: Session = Depends(get_db)):
    user = crud.get_user(db, po.created_by)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != UserRole.CREATOR:
        raise HTTPException(status_code=403, detail="Only creators can create POs")
    return crud.create_po(db, po)


@router.patch("/{po_id}", response_model=schemas.POResponse)
def update_po(po_id: int, updates: schemas.POUpdate, user_id: int, db: Session = Depends(get_db)):
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    if po.status != POStatus.NEEDS_REWORK:
        raise HTTPException(status_code=400, detail="PO can only be edited when status is Needs Rework")
    if po.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the creator can edit this PO")
    return crud.update_po(db, po, updates)