```markdown
# TRMS Backend Setup

## Setup Instructions
1. **Install Python 3.10+**: Download from python.org or use `pyenv`.
2. **Install PostgreSQL**: Run locally or use Docker:
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=your_password postgres
   ```
3. **Create Database**:
   ```bash
   psql -U postgres -h localhost
   CREATE DATABASE trms;
   ```
4. **Set Up Firebase**:
   - Create a Firebase project at console.firebase.google.com.
   - Download the service account JSON (e.g., `trms-firebase-adminsdk.json`).
   - Set path in .env: `FIREBASE_CRED_PATH=/path/to/trms-firebase-adminsdk.json`.
5. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
6. **Update .env**:
   - Add: `FIREBASE_CRED_PATH=/path/to/your/firebase-adminsdk.json`.
   - Ensure: `DATABASE_URL=postgresql://postgres:your_password@localhost:5432/trms`.
7. **Initialize Database**:
   ```python
   from app.database import Base, engine
   Base.metadata.create_all(bind=engine)
   ```
8. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
9. **Test**:
   - Visit http://localhost:8000/docs for Swagger UI.
   - Test /rent-cycles/: POST with `{"room_id": 1, "tenant_id": 1, "start_date": "2025-10-01T00:00:00+01:00", "end_date": "2025-10-31T23:59:59+01:00", "amount": 500.0}`.
   - Test /payments/: POST with `{"rent_cycle_id": 1, "tenant_id": 1, "amount": 500.0}`.
   - Get Firebase token for auth (use Firebase Auth REST API or Flutter).
   - Run tests: `pytest tests/test_rent_cycles.py` or `pytest tests/test_payments.py` (use real token).

## Notes
- Phase 4 adds RentCycle and Payment management.
- Next: Add reporting or Flutter integration.
```