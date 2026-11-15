# SPECTRE — API Contracts & Endpoint Specifications

This document defines the formal REST API contract for the **SPECTRE** backend system, established by **Member 1 (Backend & Integration)**. All endpoints adhere to standard HTTP status conventions, JSON payloads, and JWT bearer authentication.

Base URL prefix: `/api/v1`

---

## 1. Authentication & User Endpoints (`/auth`)

### 1.1 Register User
- **Method**: `POST`
- **Path**: `/api/v1/auth/register`
- **Auth**: None (Public)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "full_name": "Rishabh Singh"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Rishabh Singh",
    "role": "user",
    "is_active": true,
    "created_at": "2026-11-15T12:00:00Z"
  }
  ```
- **Errors**: `400 Bad Request` (Validation error), `409 Conflict` (Email already registered).

### 1.2 Login
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Auth**: None (Public)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "Rishabh Singh",
      "role": "user"
    }
  }
  ```
- **Errors**: `401 Unauthorized` (Invalid credentials).

### 1.3 Get Current User Profile
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Auth**: Bearer Token
- **Response**: `200 OK` (User object)

---

## 2. Conversation & AI Query Orchestration (`/conversations`)

### 2.1 List User Conversations
- **Method**: `GET`
- **Path**: `/api/v1/conversations`
- **Auth**: Bearer Token
- **Response**: `200 OK`
  ```json
  [
    {
      "id": 101,
      "title": "Query regarding defective smartphone refund",
      "legal_domain": "consumer",
      "message_count": 4,
      "created_at": "2026-11-15T12:10:00Z",
      "updated_at": "2026-11-15T12:15:00Z"
    }
  ]
  ```

### 2.2 Create Conversation
- **Method**: `POST`
- **Path**: `/api/v1/conversations`
- **Auth**: Bearer Token
- **Request Body**:
  ```json
  {
    "title": "Consumer complaint procedure",
    "legal_domain": "consumer"
  }
  ```
- **Response**: `201 Created`

### 2.3 Send Legal Query within Conversation (Core AI Orchestration)
- **Method**: `POST`
- **Path**: `/api/v1/conversations/{id}/query`
- **Auth**: Bearer Token
- **Request Body**:
  ```json
  {
    "question": "The seller refused to replace a defective electronic item under warranty. What legal actions can I take under Indian consumer law?",
    "top_k": 5
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "conversation_id": 101,
    "user_message_id": 201,
    "assistant_message_id": 202,
    "status": "answered",
    "legal_domain": "consumer",
    "answer": "Under the Consumer Protection Act, 2019 [S1], a consumer facing deficiency in goods or services is entitled to seek replacement, refund, or compensation...",
    "procedural_steps": [
      "Issue a formal legal notice to the manufacturer/seller giving 15-30 days to resolve.",
      "Lodge an online complaint on the National Consumer Helpline (NCH / INGRAM portal).",
      "If unresolved, file an e-complaint via E-Daakhil before the District Consumer Disputes Redressal Commission."
    ],
    "citations": [
      {
        "source_id": "S1",
        "document": "Consumer Protection Act, 2019",
        "section": "Section 35 & 84",
        "quote": "A complaint, in relation to any goods sold or delivered or agreed to be sold or delivered...",
        "verified": true
      }
    ],
    "confidence": 0.92,
    "confidence_label": "high",
    "disclaimer": "DISCLAIMER: This information is provided for informational and educational purposes only and does not constitute professional legal advice. Consult a licensed advocate for case-specific representation.",
    "helplines": [
      "National Consumer Helpline: 1915 or SMS 8800001915"
    ]
  }
  ```

---

## 3. Legal References & Precedents (`/references`)

### 3.1 Search Legal References
- **Method**: `GET`
- **Path**: `/api/v1/references?domain=consumer&search=defective+goods&page=1&limit=20`
- **Auth**: Optional / Public
- **Response**: `200 OK`
  ```json
  {
    "total": 1,
    "page": 1,
    "limit": 20,
    "items": [
      {
        "id": 1,
        "title": "Consumer Protection Act, 2019",
        "citation": "Act No. 35 of 2019",
        "source": "Ministry of Law and Justice, Govt of India",
        "legal_domain": "consumer",
        "year": 2019,
        "url": "https://consumeraffairs.nic.in",
        "status": "active",
        "summary": "An Act to provide for protection of the interests of consumers and for the establishment of authorities for timely settlement of disputes."
      }
    ]
  }
  ```

---

## 4. Legal Procedure Guidance (`/procedures`)

### 4.1 List Supported Procedures
- **Method**: `GET`
- **Path**: `/api/v1/procedures`
- **Auth**: Public
- **Response**: List of step-by-step procedure guides.

### 4.2 Get Procedure Detail
- **Method**: `GET`
- **Path**: `/api/v1/procedures/{slug}`
- **Auth**: Public
- **Response**: `200 OK` with prerequisites, required documents, jurisdiction notes, timeline, and step breakdown.

---

## 5. Document Templates (`/templates`)

### 5.1 List Templates
- **Method**: `GET`
- **Path**: `/api/v1/templates?category=consumer`
- **Auth**: Public
- **Response**: List of templates with metadata.

### 5.2 Render / Customize Template
- **Method**: `POST`
- **Path**: `/api/v1/templates/{id}/render`
- **Auth**: Bearer Token
- **Request Body**:
  ```json
  {
    "variables": {
      "complainant_name": "Rishabh Singh",
      "opposite_party": "XYZ Electronics Pvt Ltd",
      "purchase_date": "2026-08-10",
      "invoice_number": "INV-9921",
      "amount_claimed": "Rs. 45,000"
    }
  }
  ```
- **Response**: `200 OK` (Rendered document text with disclaimer).

---

## 6. Administration & Auditing (`/admin`)

- `GET /api/v1/admin/overview`: System statistics, query volumes, domain distribution.
- `GET /api/v1/admin/users`: List registered users (Admin only).
- `GET /api/v1/admin/audit-logs`: Audit trail of administrative actions.
- `POST /api/v1/admin/references`: Create or update legal reference.
- `POST /api/v1/admin/templates`: Create or update document template.

---

## 7. System Health & Observability (`/system`)

- `GET /health`: Liveness probe (`{"status": "ok"}`).
- `GET /api/v1/system/readiness`: Readiness probe checking database connectivity and AI engine status.
- `GET /api/v1/system/info`: Application version, runtime metadata, environment info.
