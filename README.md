# SPECTRE — AI-Based Legal Assistant, e-Lawyer and Case Guidance System

[![Tests Status](https://img.shields.io/badge/tests-69%20passed-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)]()
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)]()
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)]()

> **PES University — Software Engineering Capstone Project (JACKFRUIT Phase 1)**  
> Engineered by Team 4 according to Software Requirements Specification (SRS v1.0).

---

## 1. System Overview

**SPECTRE** is an end-to-end AI-powered legal assistant and case guidance system specifically tailored for the **Indian Legal Framework**. It provides citizens, litigants, and advocates with plain-language explanations of legal remedies, procedural step-by-step guidance, authoritative statutory citations (such as Bharatiya Nagarik Suraksha Sanhita 2023, Bharatiya Nyaya Sanhita 2023, Consumer Protection Act 2019, Information Technology Act 2000, and RTI Act 2005), and starter legal document templates.

---

## 2. Team Architecture & Responsibilities

The system is designed with strict separation of concerns across 4 specialized roles:

| Member | Project Role | Responsibilities & Ownership |
|---|---|---|
| **Rishabh** | **Project Integration** | Overall system integration, cross-module contracts, routing harmonization, static packaging, end-to-end verification, and release. |
| **Dushyanth and Rishabh** | **Backend Developer** | FastAPI orchestrator, SQLAlchemy ORM, SQLite/PostgreSQL database, JWT authentication, user and conversation repositories. |
| **Shonit** | **AI/ML Developer** | Query classification, ChromaDB vector store, RAG retrieval pipeline, citation verification, safety moderation, and `SpectreService`. |
| **Shashwat** | **Frontend Developer** | React 18 single-page application, Vite build system, Chat UI, Document Template preview/download, Admin dashboard, and HTTP/Mock API clients. |

---

## 3. End-to-End Integration Architecture

```
                  +-------------------------------------------------+
                  |          React 18 + Vite Frontend               |
                  |  (Chat UI, Templates, Dashboard, Admin Panel)  |
                  +-------------------------------------------------+
                                       |
                   HTTP / REST (JSON)  |  (VITE_USE_MOCK=false)
                                       v
                  +-------------------------------------------------+
                  |         FastAPI Backend Orchestrator            |
                  |   - Dual-Mounted API: /api/v1 and /api          |
                  |   - Unified /api/query route                    |
                  |   - Auth, RBAC, Rate Limits, Audit Trail        |
                  |   - Static UI Mount (/ui)                       |
                  +-------------------------------------------------+
                         /                       \
                        /                         \
                       v                           v
+-------------------------------+   +------------------------------------+
|   SQLAlchemy Database Engine   |   |        AI Engine & Pipeline        |
|  - Users & Roles (RBAC)       |   |  - Query Classifier                |
|  - Conversations & Messages   |   |  - ChromaDB Vector Store & BAAI    |
|  - Statutory Legal References |   |  - Citation Verification           |
|  - Document Templates         |   |  - Safety Refusal / Guardrails     |
|  - Knowledge Base Entries     |   |  - Resilient Fallback Engine       |
|  - Administrative Audit Logs  |   +------------------------------------+
+-------------------------------+
```

### Key Integration Highlights
1. **AI RAG Pipeline Mounted at Root (`ai/`)**: Member 3's pipeline (classifier, ChromaDB embeddings, citation verification, and generator) is fully integrated into the root `ai/` package and consumed by `backend/app/services/ai_client.py`.
2. **Resilient Statutory Fallback (NFR-QUAL-02)**: When offline or if local LLM instances are unavailable, `AIServiceClient` automatically engages a verified statutory knowledge base with real Indian acts (BNS, BNSS, IT Act, CPA, RTI), preventing unhandled downtime.
3. **Unified Frontend Contract (`POST /api/query`)**: Supports both authenticated users (with conversation persistence) and guest users (with anonymous instant legal guidance).
4. **Comprehensive Admin Dashboard**: Full CRUD support for Legal References, Document Templates, Legal Knowledge Entries, User Roles/Status, and Audit Trail logs.
5. **Mandatory Safety Disclaimer Enforcement (REQ-SAFE-01 to 06)**: Every legal response strictly incorporates statutory legal disclaimers and emergency helplines where distress or crime is detected.

---

## 4. Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### Automated Launch (Recommended)
Run the dev launcher script:
```powershell
# Windows PowerShell
.\run_dev.ps1
```
or
```cmd
# Windows Command Prompt
run_dev.bat
```

### Manual Launch

#### 1. Backend Orchestrator
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- API Endpoint: `http://localhost:8000`
- Swagger Interactive Docs: `http://localhost:8000/docs`
- Production UI Build: `http://localhost:8000/ui`

#### 2. Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
- Frontend Web App: `http://localhost:5173`

---

## 5. Seed Accounts & Credentials

The database automatically initializes with sample accounts and data on first startup:

| Account Type | Email | Password | Role |
|---|---|---|---|
| **Demo User** | `demo@spectre.dev` | `demo1234` | Regular Citizen |
| **System Admin** | `admin@spectre.dev` | `admin123` | Administrator |
| **Admin Legal** | `admin@spectre.legal` | `Admin@SPECTRE2026!` | Administrator |
| **Advocate** | `lawyer@spectre.legal` | `Lawyer@SPECTRE2026!` | Verified Advocate |
| **Citizen** | `citizen@spectre.legal` | `User@SPECTRE2026!` | Regular Citizen |

---

## 6. Verification and Testing

The project includes 69 automated tests covering backend APIs, AI algorithms, RAG retrieval, citations, and end-to-end integration:

```bash
# Run all tests across Backend and AI engine
python -m pytest backend/tests ai/tests

# Run end-to-end full stack integration tests
python -m pytest backend/tests/test_full_integration.py

# Build frontend production bundle
cd frontend && npm run build
```

---

## 7. Project Directory Structure

```
SPECTRE/
├── ai/                          # Member 3: AI/ML Engine, RAG & Vector Store
│   ├── classifier/              # Domain intent classification
│   ├── data/                    # ChromaDB vector database & legal PDFs
│   ├── generation/              # Prompt templates & LLM generation
│   ├── ingestion/               # Text splitters & document extraction
│   ├── retrieval/               # Embeddings & ChromaDB vector search
│   ├── safety/                  # Citation verification & safety filters
│   ├── service.py               # SpectreService entrypoint
│   └── tests/                   # 48 AI unit & integration tests
│
├── backend/                     # Member 1 & 2: FastAPI Backend Orchestrator
│   ├── app/
│   │   ├── api/v1/              # Auth, Conversations, Admin, Templates, Refs
│   │   ├── core/                # Configuration, JWT security
│   │   ├── database/            # SQLAlchemy session & seed data
│   │   ├── models/              # User, Conversation, Message, Knowledge, etc.
│   │   ├── repositories/        # Database queries & CRUD
│   │   ├── schemas/             # Pydantic DTOs & response schemas
│   │   ├── services/            # Conversation, Auth, Audit, Safety, AI Client
│   │   └── main.py              # App lifecycle, routers, CORS & UI mount
│   └── tests/                   # 21 Backend & Full-Stack integration tests
│
├── frontend/                    # Member 4: React 18 + Vite Web Application
│   ├── src/
│   │   ├── api/                 # httpApi.js (real backend client) & mockApi.js
│   │   ├── components/          # Layout, Chat, ResponseView, ResourceManager
│   │   ├── context/             # AuthContext (JWT state)
│   │   └── pages/               # Dashboard, Chat, Templates, Admin, History
│   └── dist/                    # Compiled production static bundle
│
├── docs/                        # Specifications & Contract Documentation
│   ├── AI-Based_Legal_Assistant_SRS_v1.0.pdf
│   └── AI_CONTRACT.md           # Formal Backend <-> AI data contract
│
├── run_dev.ps1                  # Single-command PowerShell full-stack runner
├── run_dev.bat                  # Single-command Batch full-stack runner
└── README.md                    # System documentation
```
