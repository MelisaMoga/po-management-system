"""
seed.py — Populează DB-ul cu date de test

Rulare (din folderul backend/):
  python seed.py

Ce creează:
- 4 useri (câte unul din fiecare rol)
- 4 PO-uri în stări diferite pentru a putea testa UI-ul fără să creezi manual
"""

import sys
import os

# Adaugă backend/ în path ca să putem importa 'app'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app import models

# Creează tabelele dacă nu există
Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    try:
        # ─── USERI ───────────────────────────────────────
        users_data = [
            {"username": "alice_creator", "role": models.UserRole.CREATOR},
            {"username": "bob_manager",   "role": models.UserRole.MANAGER},
            {"username": "carol_it",      "role": models.UserRole.IT_REP},
            {"username": "dave_finance",  "role": models.UserRole.FINANCE},
        ]

        created_users = {}
        for u_data in users_data:
            existing = db.query(models.User).filter(
                models.User.username == u_data["username"]
            ).first()

            if not existing:
                user = models.User(**u_data)
                db.add(user)
                db.commit()
                db.refresh(user)
                created_users[u_data["username"]] = user
                print(f"  ✓ User created: {user.username} ({user.role})")
            else:
                created_users[u_data["username"]] = existing
                print(f"  - User already exists: {existing.username}")

        creator = created_users["alice_creator"]

        # ─── PURCHASE ORDERS ─────────────────────────────
        pos_data = [
            {
                "title": "Office Chair x5",
                "description": "Ergonomic chairs for the new office",
                "amount": 750.00,
                "category": models.POCategory.OFFICE_SUPPLIES,
                "status": models.POStatus.PENDING_MANAGER_APPROVAL,
            },
            {
                "title": "MacBook Pro M4",
                "description": "Development laptop for new engineer",
                "amount": 2500.00,
                "category": models.POCategory.IT_EQUIPMENT,
                "status": models.POStatus.PENDING_IT_VALIDATION,
            },
            {
                "title": "Coffee Subscription",
                "description": "Monthly coffee service — under $100 so bypasses manager",
                "amount": 45.00,
                "category": models.POCategory.SERVICES,
                "status": models.POStatus.PENDING_FINANCE_APPROVAL,
            },
            {
                "title": "Pens and Notebooks",
                "description": "Rejected and needs rework",
                "amount": 120.00,
                "category": models.POCategory.OFFICE_SUPPLIES,
                "status": models.POStatus.NEEDS_REWORK,
                "rejection_reason": "Please provide more detail on quantity needed",
            },
        ]

        for po_data in pos_data:
            existing = db.query(models.PurchaseOrder).filter(
                models.PurchaseOrder.title == po_data["title"]
            ).first()

            if not existing:
                po = models.PurchaseOrder(created_by=creator.id, **po_data)
                db.add(po)
                db.commit()
                db.refresh(po)

                # Audit log pentru fiecare PO
                log = models.AuditLog(
                    po_id=po.id,
                    action="Created (seed data)",
                    performed_by=creator.id,
                    note=f"Seeded at status: {po.status}"
                )
                db.add(log)
                db.commit()

                print(f"  ✓ PO created: '{po.title}' | ${po.amount} | {po.status}")
            else:
                print(f"  - PO already exists: '{existing.title}'")

        print("\n✅ Seed completed successfully!")
        print("\nUseri disponibili:")
        for username, user in created_users.items():
            print(f"  ID={user.id}  {user.username:20} role={user.role}")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding database...\n")
    seed()
