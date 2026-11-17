# SPECTRE Full-Stack Development Runner
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  SPECTRE: AI Legal Assistant & Case Guidance System      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "Starting FastAPI Backend Orchestrator on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --reload --port 8000"

Write-Host "Starting React + Vite Frontend on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Servers launched successfully!" -ForegroundColor Green
Write-Host "  - Frontend UI:       http://localhost:5173" -ForegroundColor White
Write-Host "  - Backend API:      http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs:         http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Integrated UI:    http://localhost:8000/ui" -ForegroundColor White
