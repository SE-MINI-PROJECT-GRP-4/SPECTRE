@echo off
echo ==========================================================
echo   SPECTRE: AI Legal Assistant ^& Case Guidance System
echo ==========================================================
echo Starting FastAPI Backend on http://localhost:8000 ...
start "SPECTRE Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo Starting Vite Frontend on http://localhost:5173 ...
start "SPECTRE Frontend" cmd /k "cd frontend && npm run dev"

echo Done!
echo Frontend: http://localhost:5173
echo Backend Docs: http://localhost:8000/docs
echo Integrated UI: http://localhost:8000/ui
