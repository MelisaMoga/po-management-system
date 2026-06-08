from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..models import UserRole, POStatus
from ..database import get_db
from .. import models

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

@router.post("/{po_id}/submit", response_model=schemas.POResponse)
def submit_po(po_id: int, user_id: int, db: Session = Depends(get_db)):
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    if po.status != models.POStatus.DRAFT and po.status != models.POStatus.NEEDS_REWORK:
        raise HTTPException(status_code=400, detail="Only Draft or Needs Rework POs can be submitted")
    if po.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the creator can submit this PO")

    # State machine - decide the first status
    new_status = crud.calculate_next_status(po)

    crud.update_po_status(db, po, new_status)
    crud.add_audit_log(db, po_id, "Submitted", user_id, f"PO submitted → {new_status.value}") # .value returns the string instead of the enum name.

    return crud.get_po(db, po_id)

@router.post("/{po_id}/approve", response_model=schemas.POResponse)
def approve_po(po_id: int, user_id: int, db: Session = Depends(get_db)):
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # verify that the user has the appropriate role for the current status
    if po.status == models.POStatus.PENDING_MANAGER_APPROVAL:
        if user.role != models.UserRole.MANAGER:
            raise HTTPException(status_code=403, detail="Only a manager can approve at this stage")
        # After the manager, we check if it's IT Equipment
        if po.category == models.POCategory.IT_EQUIPMENT:
            new_status = models.POStatus.PENDING_IT_VALIDATION
        else:
            new_status = models.POStatus.PENDING_FINANCE_APPROVAL

    elif po.status == models.POStatus.PENDING_IT_VALIDATION:
        if user.role != models.UserRole.IT_REP:
            raise HTTPException(status_code=403, detail="Only an IT rep can approve at this stage")
        new_status = models.POStatus.PENDING_FINANCE_APPROVAL

    elif po.status == models.POStatus.PENDING_FINANCE_APPROVAL:
        if user.role != models.UserRole.FINANCE:
            raise HTTPException(status_code=403, detail="Only a finance user can approve at this stage")
        new_status = models.POStatus.INVOICED

    else:
        raise HTTPException(status_code=400, detail=f"PO cannot be approved at status: {po.status}")

    crud.update_po_status(db, po, new_status)
    crud.add_audit_log(db, po_id, f"Approved by {user.role.value}", user_id, f"Status → {new_status}")

    return crud.get_po(db, po_id)

@router.post("/{po_id}/reject", response_model=schemas.POResponse)
def reject_po(po_id: int, user_id: int, reason: str, db: Session = Depends(get_db)):
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if po.status == models.POStatus.PENDING_MANAGER_APPROVAL:
        if user.role != models.UserRole.MANAGER:
            raise HTTPException(status_code=403, detail="Only a manager can reject at this stage")
    elif po.status == models.POStatus.PENDING_IT_VALIDATION:
        if user.role != models.UserRole.IT_REP:
            raise HTTPException(status_code=403, detail="Only an IT rep can reject at this stage")
    elif po.status == models.POStatus.PENDING_FINANCE_APPROVAL:
        if user.role != models.UserRole.FINANCE:
            raise HTTPException(status_code=403, detail="Only a finance user can reject at this stage")
    else:
        raise HTTPException(status_code=400, detail=f"PO cannot be rejected at status: {po.status}")

    crud.update_po_status(db, po, models.POStatus.NEEDS_REWORK, rejection_reason=reason)
    crud.add_audit_log(db, po_id, f"Rejected by {user.role.value}", user_id, reason)

    return crud.get_po(db, po_id)

@router.post("/{po_id}/resubmit", response_model=schemas.POResponse)
def resubmit_po(po_id: int, user_id: int, db: Session = Depends(get_db)):
    po = crud.get_po(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    if po.status != models.POStatus.NEEDS_REWORK:
        raise HTTPException(status_code=400, detail="Only Needs Rework POs can be resubmitted")
    if po.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the creator can resubmit this PO")

    # Resubmit repornește fluxul de la început - aceeași logică ca submit
    new_status = crud.calculate_next_status(po)

    crud.update_po_status(db, po, new_status)
    crud.add_audit_log(db, po_id, "Resubmitted", user_id, f"PO resubmitted → {new_status.value}")

    return crud.get_po(db, po_id)