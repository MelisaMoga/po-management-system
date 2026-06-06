import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class UserRole(str, enum.Enum):
    CREATOR = "creator"
    MANAGER = "manager"
    IT_REP = "it_rep"
    FINANCE = "finance"


class POCategory(str, enum.Enum):
    SERVICES = "Services"
    OFFICE_SUPPLIES = "Office Supplies"
    IT_EQUIPMENT = "IT Equipment"


class POStatus(str, enum.Enum):
    DRAFT = "Draft"
    PENDING_MANAGER_APPROVAL = "Pending Manager Approval"
    PENDING_IT_VALIDATION = "Pending IT Validation"
    PENDING_FINANCE_APPROVAL = "Pending Finance Approval"
    INVOICED = "Invoiced"
    NEEDS_REWORK = "Needs Rework"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    purchase_orders = relationship("PurchaseOrder", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="performed_by_user")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(Enum(POCategory), nullable=False)
    status = Column(Enum(POStatus), default=POStatus.DRAFT, nullable=False)
    rejection_reason = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", back_populates="purchase_orders")
    audit_logs = relationship("AuditLog", back_populates="purchase_order", order_by="AuditLog.timestamp")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    action = Column(String(100), nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    purchase_order = relationship("PurchaseOrder", back_populates="audit_logs")
    performed_by_user = relationship("User", back_populates="audit_logs")