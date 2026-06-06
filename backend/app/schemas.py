from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import UserRole, POCategory, POStatus


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    role: UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    model_config = {"from_attributes": True}


class POCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    category: POCategory
    created_by: int


class POUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[POCategory] = None


class AuditLogResponse(BaseModel):
    id: int
    action: str
    note: Optional[str]
    timestamp: datetime
    performed_by_user: UserResponse

    model_config = {"from_attributes": True}


class POResponse(BaseModel):
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
    id: int
    title: str
    amount: float
    category: POCategory
    status: POStatus
    created_at: datetime
    creator: UserResponse

    model_config = {"from_attributes": True}