@echo off
REM CISSP Study Companion — start backend and frontend locally
set ROOT=%~dp0
set PORT=8001

echo.
echo  ========================================
echo   CISSP STUDY COMPANION — LOCAL DEV
echo  ========================================
echo.

powershell -NoProfile -Command "$c = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if ($c) { Write-Host 'ERROR: Port %PORT% is already in use (PID' $c.OwningProcess ').'; Write-Host 'Close the other CISSP Backend window or run: Stop-Process -Id' $c.OwningProcess '-Force'; exit 1 }"
if errorlevel 1 (
  echo.
  pause
  exit /b 1
)

echo [1/2] Starting backend on http://127.0.0.1:%PORT% ...
start "CISSP Backend" cmd /k "cd /d "%ROOT%backend" && (if not exist .venv python -m venv .venv) && .venv\Scripts\activate && pip install -r requirements.txt -q && uvicorn app.main:app --reload --host 127.0.0.1 --port %PORT%"

timeout /t 3 /nobreak > nul

echo [2/2] Starting frontend on http://localhost:5173 ...
start "CISSP Frontend" cmd /k "cd /d "%ROOT%frontend" && (if not exist node_modules npm install) && npm run dev"

echo.
echo  Open http://localhost:5173 in your browser.
echo  Backend API docs: http://127.0.0.1:%PORT%/docs
echo.
echo  Note: pip upgrade notices are harmless and can be ignored.
echo.
echo  Press any key to close this window (servers keep running).
pause > nul
