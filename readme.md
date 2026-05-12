```markdown
# Propti Backend

Propti is a FastAPI backend for rental property management. It provides REST APIs for managing properties, rooms, tenants, rent cycles, payments, reminders, reports, and Firebase authentication.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run](#run)
- [API Documentation](#api-documentation)
- [Health Check](#health-check)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Notes](#notes)

## Overview

The Propti backend supports landlord workflows with APIs for:

- Property and room management
- Tenant and guarantor tracking
- Rent cycle scheduling
- Payment processing and status tracking
- Reminder generation
- Reporting and PDF generation
- Firebase-backed authentication

## Features

- CRUD endpoints for properties, rooms, tenants, rent cycles, payments, landlords, reminders, and reports
- Automatic database table creation on startup
- Firebase authentication integration
- CORS enabled for all origins
- Swagger and ReDoc API documentation
- Production-ready server support via Gunicorn

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- Firebase Admin SDK
- Pydantic
- ReportLab
- APScheduler
- pytest

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or newer
- Git
- Firebase project with a service account key

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Propti_backend
```

2. Create and activate a Python virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following values:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/propti_db
FIREBASE_CRED_PATH=./rentra.json
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

### Firebase setup

1. Open the Firebase Console.
2. Create or select a project.
3. Navigate to Project Settings → Service Accounts.
4. Generate a new private key.
5. Save the JSON key as `rentra.json` in the project root.

### Create the database

```bash
psql -U postgres -h localhost
CREATE DATABASE propti_db;
\q
```

## Run

Start the server in development mode:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start the app with Gunicorn for a production-like environment:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Health Check

- `GET /` - returns service status and metadata
- `GET /health` - returns basic health status

## Project Structure

```
Propti_backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── agreements.py
│   │       ├── auth.py
│   │       ├── landlords.py
│   │       ├── media.py
│   │       ├── payments.py
│   │       ├── properties.py
│   │       ├── reminders.py
│   │       ├── rent_cycles.py
│   │       ├── reports.py
│   │       ├── rooms.py
│   │       └── tenants.py
│   ├── crud/
│   └── utils/
├── requirements.txt
├── rentra.json
├── readme.md
└── README_COMPREHENSIVE.md
```

## Testing

Run the test suite:

```bash
pytest
```

## Notes

- The app automatically creates database tables at startup.
- Ensure `DATABASE_URL` and `FIREBASE_CRED_PATH` are set before launching the server.
- Use the Swagger UI to explore and test the API endpoints.
```