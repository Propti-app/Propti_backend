from fastapi import FastAPI
from .api.routers import properties, auth, rooms, tenants, rent_cycles, payments, landlords, reminders, reports
from .database import Base, engine
import time

app = FastAPI(title="Propti backend")

# Startup event for DB initialization
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(properties)
app.include_router(auth)
app.include_router(rooms)
app.include_router(tenants)
app.include_router(rent_cycles)
app.include_router(payments)
app.include_router(landlords)
app.include_router(reminders)
app.include_router(reports)

@app.get("/")
def root():
    """Health check endpoint - keeps server warm"""
    return {
        "status": "healthy",
        "service": "Propti API",
        "timestamp": time.time()
    }

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    """Simple health check"""
    return {"status": "ok"}





















