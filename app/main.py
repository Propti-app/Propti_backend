# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routers import (
    properties, auth, rooms, tenants, rent_cycles,
    payments, landlords, reminders, reports,
)
from .api.routers.agreements import router as agreements_router
from .api.routers.media      import router as media_router
from .database import Base, engine
import time

app = FastAPI(
    title="Propti API",
    description="Accountability platform for landlords in Cameroon",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# ── Existing routers ──────────────────────────────────────────────────────────
app.include_router(properties)
app.include_router(auth)
app.include_router(rooms)
app.include_router(tenants)
app.include_router(rent_cycles)
app.include_router(payments)
app.include_router(landlords)
app.include_router(reminders)
app.include_router(reports)

# ── New routers ───────────────────────────────────────────────────────────────
app.include_router(agreements_router)  # /agreements/*
app.include_router(media_router)       # /media/*


@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "Propti API v2",
        "features": ["agreements", "appwrite_media", "fcm_notifications"],
        "timestamp": time.time(),
    }


@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}












