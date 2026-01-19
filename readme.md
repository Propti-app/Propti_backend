# Propti Backend

A comprehensive property management system built with FastAPI and SQLAlchemy. Propti helps landlords manage properties, rooms, tenants, rent cycles, and payments with ease.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Database Models](#database-models)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Development](#development)

## Overview

Propti is a backend service designed to manage the complete lifecycle of rental properties. It provides APIs for:

- **Property Management**: Create and manage multiple properties
- **Room Management**: Track rooms within properties with rent amounts and due dates
- **Tenant Management**: Store comprehensive tenant information including contact details and guarantor information
- **Rent Cycle Management**: Define rental periods and track rent amounts
- **Payment Processing**: Record and track tenant payments with multiple payment methods
- **Reminders**: Automated payment reminders for tenants
- **Reporting**: Generate comprehensive rent and payment reports
- **Authentication**: Secure landlord authentication using Firebase

## Features

✨ **Core Functionality:**
- Multi-property management
- Room and tenant tracking
- Automated rent cycle creation
- Payment tracking with status management (Paid, Partial, Overdue)
- Multiple payment methods support (Cash, Mobile Money, Bank)
- Payment reminders and notifications
- Comprehensive reporting capabilities
- Tenant archival and historical tracking
- Landlord settings and preferences

🔐 **Security:**
- Firebase Authentication integration
- Role-based access control
- Secure password hashing (bcrypt)
- JWT token support

📊 **Reporting:**
- Payment status reports
- Rent collection analytics
- Tenant balance tracking
- PDF report generation using ReportLab

## Tech Stack

**Backend Framework:**
- FastAPI 0.115.0 - Modern web framework
- Uvicorn 0.30.6 - ASGI server

**Database:**
- PostgreSQL - Primary database
- SQLAlchemy 2.0.31 - ORM
- psycopg2-binary - PostgreSQL adapter

**Authentication & Security:**
- Firebase Admin SDK 6.5.0
- bcrypt 4.2.0 - Password hashing
- Passlib 1.7.4 - Password utilities
- Pydantic 2.8.2 - Data validation

**Additional Libraries:**
- APScheduler 3.10.4 - Job scheduling for reminders
- ReportLab 4.0.4 - PDF report generation
- email-validator 2.2.0 - Email validation
- python-dateutil 2.9.0 - Date utilities
- python-dotenv 1.0.1 - Environment variables

**Testing & Development:**
- pytest 8.3.3 - Testing framework
- Gunicorn 21.2.0 - Production server

## Prerequisites

- **Python 3.10 or higher**
- **PostgreSQL 12+** (or Docker)
- **Git**
- **Firebase Project** (for authentication)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Propti_backend
```

### 2. Install Python & Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install PostgreSQL

**Option A: Local Installation**
```bash
# On Windows (using chocolatey):
choco install postgresql

# On macOS (using brew):
brew install postgresql
```

**Option B: Docker**
```bash
docker run -d \
  --name propti-postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=propti_db \
  postgres:15
```

### 4. Create Database

```bash
psql -U postgres -h localhost
CREATE DATABASE propti_db;
\q
```

### 5. Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or select existing one
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file as `rentra.json` in the project root (already included in this repo)

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Create Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/propti_db

# Firebase Configuration
FIREBASE_CRED_PATH=./rentra.json

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development
```

### Configure Database Connection

Update `DATABASE_URL` in `.env` with your PostgreSQL credentials:

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

## Project Structure

```
Propti_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── database.py                # Database configuration & session management
│   ├── models.py                  # SQLAlchemy ORM models
│   ├── schemas.py                 # Pydantic validation schemas
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/               # API endpoints
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── landlords.py       # Landlord management
│   │       ├── properties.py      # Property CRUD operations
│   │       ├── rooms.py           # Room management
│   │       ├── tenants.py         # Tenant management
│   │       ├── rent_cycles.py     # Rent cycle management
│   │       ├── payments.py        # Payment processing
│   │       ├── reminders.py       # Payment reminders
│   │       └── reports.py         # Reporting endpoints
│   │
│   ├── crud/                      # Database operations (CRUD)
│   │   ├── landlord.py
│   │   ├── property.py
│   │   ├── room.py
│   │   ├── tenant.py
│   │   ├── rent_cycle.py
│   │   ├── payment.py
│   │   ├── reminder.py
│   │   └── report.py
│   │
│   ├── utils/
│   │   └── auth.py                # Authentication utilities
│   │
│   └── tests/
│       ├── test_properties.py
│       └── test_rent_cycles.py
│
├── requirements.txt               # Python dependencies
├── rentra.json                    # Firebase service account key
├── readme.md                      # Original setup guide
└── test.py                        # Quick test script
```

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main API Endpoints

#### Authentication
- `POST /auth/login` - Login with credentials
- `POST /auth/register` - Register new landlord
- `POST /auth/firebase-sync` - Sync Firebase user to database

#### Properties
- `POST /properties/` - Create property
- `GET /properties/` - List properties
- `GET /properties/{id}` - Get property details
- `PUT /properties/{id}` - Update property
- `DELETE /properties/{id}` - Delete property

#### Rooms
- `POST /rooms/` - Create room
- `GET /rooms/{property_id}` - List rooms
- `PUT /rooms/{id}` - Update room
- `DELETE /rooms/{id}` - Delete room

#### Tenants
- `POST /tenants/` - Add tenant
- `GET /tenants/` - List tenants
- `GET /tenants/{id}` - Get tenant details
- `PUT /tenants/{id}` - Update tenant
- `DELETE /tenants/{id}` - Archive tenant

#### Rent Cycles
- `POST /rent-cycles/` - Create rent cycle
- `GET /rent-cycles/{room_id}` - Get cycle details
- `PUT /rent-cycles/{id}` - Update cycle
- `DELETE /rent-cycles/{id}` - Delete cycle

#### Payments
- `POST /payments/` - Record payment
- `GET /payments/{rent_cycle_id}` - List cycle payments
- `PUT /payments/{id}` - Update payment
- `DELETE /payments/{id}` - Delete payment

#### Reminders
- `POST /reminders/` - Create reminder
- `GET /reminders/` - List reminders
- `PUT /reminders/{id}` - Update reminder status

#### Reports
- `GET /reports/rent-summary` - Rent collection summary
- `GET /reports/tenant-balances` - Tenant balance report
- `GET /reports/payment-status` - Payment status report
- `GET /reports/property/{id}/pdf` - Generate PDF report

## Database Models

### Core Entities

**Landlord**
- Stores landlord information with Firebase authentication support
- Manages settings and preferences
- Links to properties

**Property**
- Represents a rental property
- Belongs to a landlord
- Contains multiple rooms

**Room**
- Individual rental unit within a property
- Tracks rent amount and due date
- Can have an assigned tenant

**Tenant**
- Stores comprehensive tenant information
- Includes contact details and guarantor information
- Tracks balance and payment status
- Can be archived for historical records

**RentCycle**
- Defines a rental period for a room
- Links tenant to room for specific dates
- Tracks rent amount for that period

**Payment**
- Records tenant payments
- Tracks amount, method, and status
- Links to rent cycle

**Reminder**
- Automated payment reminders
- Tracks send status
- Can be scheduled

**Report**
- Generated reports for landlords
- Includes payment summaries and analytics
- Exportable as PDF

## Running the Application

### Development Mode

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

### Production Mode

```bash
# Using Gunicorn (recommended for production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest app/tests/test_properties.py
pytest app/tests/test_rent_cycles.py
```

### Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Example Test Request

Test the rent cycle endpoint:

```bash
curl -X POST http://localhost:8000/rent-cycles/ \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "tenant_id": 1,
    "start_date": "2025-10-01T00:00:00+01:00",
    "end_date": "2025-10-31T23:59:59+01:00",
    "amount": 500.0
  }'
```

## Development

### Code Style & Quality

This project uses:
- **Type hints** for better code clarity
- **Pydantic** for request/response validation
- **SQLAlchemy ORM** for database abstraction
- **FastAPI dependency injection** for clean architecture

### Database Migrations

Currently, the database schema is created automatically on startup via SQLAlchemy:

```python
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
```

For production migrations, consider implementing Alembic.

### Adding New Endpoints

1. Create schema in `app/schemas.py`
2. Create CRUD operations in `app/crud/`
3. Create router in `app/api/routers/`
4. Include router in `app/main.py`

Example:

```python
# schemas.py
class MyResourceCreate(BaseModel):
    name: str

# crud/my_resource.py
def create_my_resource(db: Session, resource: schemas.MyResourceCreate):
    db_resource = models.MyResource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

# api/routers/my_resource.py
@router.post("/", response_model=schemas.MyResourceResponse)
def create(resource: schemas.MyResourceCreate, db: Session = Depends(get_db)):
    return crud.create_my_resource(db, resource)
```

### Troubleshooting

**Database Connection Error**
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists

**Firebase Authentication Issues**
- Verify `rentra.json` path in `.env`
- Check Firebase service account has proper permissions
- Ensure Firebase project is configured correctly

**Module Import Errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python path includes project root

## Next Steps

- Implement Alembic for database migrations
- Add comprehensive unit test coverage
- Implement caching with Redis
- Add email notification service
- Create Flutter mobile client
- Set up CI/CD pipeline with GitHub Actions

## License

This project is proprietary and confidential.

## Contact & Support..

For issues or questions, please contact the development team.
