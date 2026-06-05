"""
schemas.py — Validarea datelor care intră și ies din API

Concepte cheie:
- Pydantic: librărie de validare. Dacă trimiți amount=-5, aruncă eroare automată.
- Schema != Model: Modelele (models.py) descriu DB. Schemele descriu ce primește/returnează API-ul.
- Separarea e importantă: nu vrei să expui câmpuri interne din DB în API.

Analogie embedded: schemele sunt ca structurile de mesaje în protocoale seriale —
definesc exact ce bytes/câmpuri sunt valide.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import UserRole, POCategory, POStatus


# ─────────────────────────────────────────────
# USER SCHEMAS
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    """Date necesare pentru crearea unui user."""
    username: str = Field(..., min_length=2, max_length=100)
    role: UserRole


class UserResponse(BaseModel):
    """Ce returnăm când cineva cere info despre un user."""
    id: int
    username: str
    role: UserRole

    # Permite Pydantic să citească atributele din obiectele SQLAlchemy (nu doar dict-uri)
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# PURCHASE ORDER SCHEMAS
# ─────────────────────────────────────────────

class POCreate(BaseModel):
    """Date necesare pentru crearea unui PO nou."""
    title: str = Field(..., min_length=1, max_length=200, description="Titlul comenzii")
    description: Optional[str] = Field(None, description="Detalii suplimentare")
    amount: float = Field(..., gt=0, description="Suma trebuie să fie pozitivă")
    category: POCategory
    created_by: int = Field(..., description="ID-ul userului care creează PO-ul")


class POUpdate(BaseModel):
    """Câmpuri editabile când PO e în starea NEEDS_REWORK."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[POCategory] = None


class AuditLogResponse(BaseModel):
    """Un rând din istoricul unui PO."""
    id: int
    action: str
    note: Optional[str]
    timestamp: datetime
    performed_by_user: UserResponse

    model_config = {"from_attributes": True}


class POResponse(BaseModel):
    """Răspunsul complet pentru un PO — include creatorul și istoricul."""
    id: int
    title: str
    description: Optional[str]
    amount: float
    category: POCategory
    status: POStatus
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    creator: UserResponse
    audit_logs: List[AuditLogResponse] = []

    model_config = {"from_attributes": True}


class POListResponse(BaseModel):
    """Versiunea simplificată pentru listare (fără audit logs)."""
    id: int
    title: str
    amount: float
    category: POCategory
    status: POStatus
    created_at: datetime
    creator: UserResponse

    model_config = {"from_attributes": True}
