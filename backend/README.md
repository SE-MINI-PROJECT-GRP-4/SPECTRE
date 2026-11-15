# SPECTRE Backend & Integration Subsystem

Technical Owner: **Member 1 — Backend & Integration**

## Overview

The SPECTRE backend is a high-performance legal orchestration engine built with **FastAPI**, **SQLAlchemy 2.0**, and **Pydantic**. It coordinates user authentication, multi-turn legal conversations, AI/RAG query dispatch, legal procedure walkthroughs, document templates, and administrative audit trails, tailored specifically for Indian law (BNS 2023, BNSS 2023, BSA 2023, CPA 2019, IT Act 2000, RTI Act 2005).

---

## Key Features

1. **Secure Authentication & RBAC**: JWT Bearer token authentication, bcrypt password hashing, and role guards (`USER`, `ADMIN`, `ADVOCATE`).
2. **AI & RAG Orchestration**: Integrates with the SPECTRE AI engine contract (`AI_CONTRACT.md`) with a built-in resilient legal retrieval engine when running offline.
3. **Safety & Compliance Layer**: Enforces mandatory statutory disclaimers (REQ-SAFE-01 to 06), suppresses false outcome guarantees, and auto-attaches emergency helpline numbers (112, 1091, 1098, 1930).
4. **Step-by-Step Procedure Guidance**: Structured actionable walkthroughs for FIR/Zero FIR, Consumer Complaints, RTI filings, and Cybercrime reporting.
5. **Document Template Customization**: Standardized legal drafts with dynamic placeholder variable rendering and warning notices.
6. **Administrative Auditing & Health Observability**: Audits all admin operations and provides liveness and readiness health checks.

---

## Architecture & Directory Layout

```
backend/
├── alembic.ini                   # Database migration config
├── alembic/                      # Alembic migrations & versions
├── app/
│   ├── main.py                   # FastAPI application factory & router mounting
│   ├── core/                     # App settings, configuration & security
│   ├── database/                 # SQLAlchemy engine, session & seed data
│   ├── models/                   # Declarative ORM models
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── repositories/             # Database CRUD repositories
│   ├── services/                 # Business logic, AI client & orchestrators
│   ├── dependencies/             # FastAPI dependency injection (auth, db)
│   └── api/v1/                   # REST API routes (auth, queries, admin, etc.)
├── tests/                        # Automated unit and security tests
├── requirements.txt              # Pinned Python package dependencies
├── Dockerfile                    # Multi-stage production container
└── docker-compose.yml            # Container deployment specification
```

---

## Quickstart

### 1. Environment Setup
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Database Migrations & Seeds
Database tables and default records (Acts, Templates, Admin) are seeded automatically on first launch, or you can run migrations manually:
```bash
alembic upgrade head
```

### 3. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at:
👉 `http://localhost:8000/docs`

---

## Running Automated Tests

```bash
pytest tests/ -v
```
