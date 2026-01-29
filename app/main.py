from fastapi import FastAPI
from .api.routers import properties, auth, rooms, tenants, rent_cycles, payments, landlords, reminders, reports
from .database import Base, engine
import time

app = FastAPI(title="Propti backend")

# Startup event for DB initialization (better than running at import time)
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

@app.get("/health")
def health_check():
    """Simple health check"""
    return {"status": "ok"}


















# from fastapi import FastAPI
# from .api.routers import properties, auth, rooms, tenants, rent_cycles, payments, landlords, reminders, reports
# from .database import Base, engine

# app = FastAPI(title="Propti backend")

# # Initialize database.
# Base.metadata.create_all(bind=engine)

# # Include routers
# app.include_router(properties)
# app.include_router(auth)
# app.include_router(rooms)
# app.include_router(tenants)
# app.include_router(rent_cycles)
# app.include_router(payments)
# app.include_router(landlords)
# app.include_router(reminders)
# app.include_router(reports)

# #__init___.py files are not needed in FastAPI apps, so they are omitted.
# @app.get("/")
# def read_root():
#     return {"message": "TRMS Backend Running"}

# @app.get("/")
# def root():
#     """Health check endpoint - keeps server warm"""
#     return {
#         "status": "healthy",
#         "service": "Propti API",
#         "timestamp": time.time()
#     }

# @app.get("/health")
# def health_check():
#     """Simple health check"""
#     return {"status": "ok"}















