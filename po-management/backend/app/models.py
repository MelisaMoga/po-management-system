"""
models.py — Definirea tabelelor din PostgreSQL ca și clase Python

Concepte cheie:
- Fiecare clasă = un tabel în DB
- Fiecare Column = o coloană în tabel
- Enum: tip de date care acceptă doar valorile predefinite (ca un enum în C/C++)
- relationship: SQLAlchemy știe să facă JOIN automat între tabele
- ForeignKey: cheie externă — leagă un rând dintr-un tabel de un rând din alt tabel

Analogie embedded: dacă în C ai struct-uri, aici ai clase cu câmpuri tipizate.
"""

import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


# ─────────────────────────────────────────────
# ENUM-uri — valorile fixe acceptate în DB
# ─────────────────────────────────────────────

class UserRole(str, enum.Enum):
    CREATOR = "creator"       # Creatorul PO-ului (oricine din companie)
    MANAGER = "manager"       # Aprobă dacă suma >= 100 USD
    IT_REP = "it_rep"         # Validează PO-urile de tip IT Equipment
    FINANCE = "finance"       # Aprobare financiară finală


class POCategory(str, enum.Enum):
    SERVICES = "Services"
    OFFICE_SUPPLIES = "Office Supplies"
    IT_EQUIPMENT = "IT Equipment"


class POStatus(str, enum.Enum):
    """
    Statusurile posibile ale unui PO — reprezintă starea din state machine.

    Flux normal:
    DRAFT → PENDING_MANAGER_APPROVAL → PENDING_IT_VALIDATION → PENDING_FINANCE_APPROVAL → INVOICED

    La orice pas de aprobare: → NEEDS_REWORK (dacă e respins)
    NEEDS_REWORK → DRAFT (când creatorul resubmite)

    Bypass-uri:
    - Suma < 100 USD: sare PENDING_MANAGER_APPROVAL
    - Categorie != IT Equipment: sare PENDING_IT_VALIDATION
    """
    DRAFT = "Draft"
    PENDING_MANAGER_APPROVAL = "Pending Manager Approval"
    PENDING_IT_VALIDATION = "Pending IT Validation"
    PENDING_FINANCE_APPROVAL = "Pending Finance Approval"
    INVOICED = "Invoiced"
    NEEDS_REWORK = "Needs Rework"


# ─────────────────────────────────────────────
# MODELE (Tabele)
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    # Relații — SQLAlchemy face JOIN automat când accesezi user.purchase_orders
    purchase_orders = relationship("PurchaseOrder", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="performed_by_user")

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(Enum(POCategory), nullable=False)
    status = Column(Enum(POStatus), default=POStatus.DRAFT, nullable=False)

    # Motivul respingerii — completat de reviewer la reject
    rejection_reason = Column(Text, nullable=True)

    # Cheie externă către tabelul users
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # server_default: valoarea default e pusă de PostgreSQL, nu de Python
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", back_populates="purchase_orders")
    audit_logs = relationship(
        "AuditLog",
        back_populates="purchase_order",
        order_by="AuditLog.timestamp"  # Audit log sortat cronologic
    )

    def __repr__(self):
        return f"<PurchaseOrder id={self.id} title={self.title} status={self.status}>"


class AuditLog(Base):
    """
    Istoricul complet al unui PO.
    Fiecare acțiune (creare, aprobare, respingere, resubmitere) e înregistrată aici.
    Aceasta este dovada că știi să gândești ca un inginer — trasabilitate completă.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    action = Column(String(100), nullable=False)   # ex: "Created", "Approved by Manager"
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=True)             # Comentariu opțional (ex: motivul respingerii)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    purchase_order = relationship("PurchaseOrder", back_populates="audit_logs")
    performed_by_user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog po_id={self.po_id} action={self.action}>"
