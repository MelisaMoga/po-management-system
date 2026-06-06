from sqlalchemy.orm import Session
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_po(db: Session, po_id: int):
    return db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == po_id).first()


def get_pos(db: Session):
    return db.query(models.PurchaseOrder).order_by(models.PurchaseOrder.created_at.desc()).all()


def create_po(db: Session, po: schemas.POCreate):
    db_po = models.PurchaseOrder(
        title=po.title,
        description=po.description,
        amount=po.amount,
        category=po.category,
        status=models.POStatus.DRAFT,
        created_by=po.created_by
    )
    db.add(db_po)
    db.commit()
    db.refresh(db_po)

    add_audit_log(db, db_po.id, "Created", po.created_by, f"PO created with amount ${po.amount:.2f}")
    return db_po


def update_po(db: Session, po: models.PurchaseOrder, updates: schemas.POUpdate):
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(po, field, value)
    db.commit()
    db.refresh(po)
    return po


def update_po_status(db: Session, po: models.PurchaseOrder, new_status: models.POStatus, rejection_reason: str = None):
    po.status = new_status
    if rejection_reason is not None:
        po.rejection_reason = rejection_reason
    else:
        po.rejection_reason = None
    db.commit()
    db.refresh(po)
    return po


def add_audit_log(db: Session, po_id: int, action: str, performed_by: int, note: str = None):
    log = models.AuditLog(po_id=po_id, action=action, performed_by=performed_by, note=note)
    db.add(log)
    db.commit()
    return log