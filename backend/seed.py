from app.database import engine, SessionLocal
from app.models import Base, User, UserRole

SEED_USERS = [
    {"username": "alice", "role": UserRole.CREATOR},
    {"username": "bob", "role": UserRole.MANAGER},
    {"username": "carol", "role": UserRole.IT_REP},
    {"username": "dave", "role": UserRole.FINANCE},
]

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    existing = {u.username for u in db.query(User).all()}
    to_insert = [User(**u) for u in SEED_USERS if u["username"] not in existing]
    if to_insert:
        db.add_all(to_insert)
        db.commit()
        print(f"Seeded {len(to_insert)} user(s).")
    else:
        print("Users already seeded, nothing to do.")
finally:
    db.close()
