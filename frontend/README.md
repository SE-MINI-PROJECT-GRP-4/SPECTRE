# SPECTRE – Frontend

Web frontend for **AI-Based Legal Assistant, e-Lawyer and Case Guidance System** (JACKFRUIT Phase-1, UE24CS341A – Software Engineering, PES University).
Built with React 18, Vite and React Router.

## Run

```bash
npm install
cp .env.example .env     # optional
npm run dev              # http://localhost:5173
npm run build            # production build into dist/
```

By default the app runs against an **in-browser mock backend** (`VITE_USE_MOCK=true`) so it works with no server.
Mock logins: `demo@spectre.dev / demo1234` (user), `admin@spectre.dev / admin123` (admin).
Set `VITE_USE_MOCK=false` to call the real backend at `VITE_API_BASE` (default `/api`, proxied to `localhost:8000` in dev).

## Screens (SRS §3.1)

| Route | Screen | Requirements |
| --- | --- | --- |
| `/login`, `/register` | Login / registration with validation | REQ-AUTH-01..05 |
| `/` | Dashboard / home | – |
| `/chat`, `/chat/:id` | Assistant chat, structured responses, sources, disclaimer | REQ-QUERY-01..12, REQ-REF-02..06, REQ-PROC-*, REQ-SAFE-* |
| `/templates` | Template list, categories, preview, download | REQ-DOC-01..04, 08 |
| `/history` | Conversation history (login required) | REQ-HIST-01..05 |
| `/admin` | Knowledge, references, templates, users, audit log (admin only) | REQ-ADMIN-01..07 |

## Backend API contract (used when `VITE_USE_MOCK=false`)

All requests send `Authorization: Bearer <token>` when logged in. JSON in/out. Errors: `{ "message": "..." }`.

| Method & path | Body | Response |
| --- | --- | --- |
| `POST /auth/register` | `{name,email,password}` | `{token,user}` |
| `POST /auth/login` | `{email,password}` | `{token,user}` |
| `POST /auth/logout`, `GET /auth/me` | – | `{user}` |
| `POST /query` | `{text,conversationId?}` | `{conversationId,userMessage,answer}` |
| `GET /conversations`, `GET /conversations/:id`, `DELETE /conversations/:id` | – | conversation(s) |
| `GET /references`, `GET /templates` | – | arrays (Appendix B shapes) |
| `GET/POST /admin/:resource`, `PUT/DELETE /admin/:resource/:id` | item | `resource` ∈ `knowledge, references, templates, users` |
| `GET /admin/audit`, `GET /admin/stats` | – | log rows / counts |

An `answer` has: `text, domain, confidence (insufficient|low|medium), procedure{prerequisites,steps}, sources[], notes[], template, disclaimer`.

## Notes

- The UI hides admin screens for non-admins, but **authorization must be enforced by the backend** (REQ-AUTH-06, NFR-SEC-03/04).
- The mock backend stores plaintext passwords in `localStorage` for demo only – never use real credentials in mock mode.
- Citations shown to users come only from stored reference records (REQ-REF-09, BR-04).
