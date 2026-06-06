from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import po, users
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PO Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(po.router, prefix="/api/po", tags=["Purchase Orders"])

@app.get("/")
def root():
    return {"status": "ok", "message": "PO Management API is running"}