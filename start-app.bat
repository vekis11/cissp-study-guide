@echo off
REM CISSP Study Companion — installable PWA (one link for phone + PC)
set ROOT=%~dp0
set PORT=8080

echo.
echo  ========================================
echo   CISSP STUDY — INSTALLABLE APP MODE
echo  ========================================
echo.

echo [1/2] Building mobile PWA frontend...
cd /d "%ROOT%frontend"
if not exist node_modules npm install
call npm run build
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo.
echo [2/2] Starting server on all network interfaces port %PORT% ...
cd /d "%ROOT%backend"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt -q
set CORS_ALLOW_ALL=true
set SERVE_STATIC=true

REM Detect LAN IP without PowerShell (works when powershell is not on PATH)
set IP=
for /f "delims=" %%i in ('.venv\Scripts\python.exe -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.settimeout(2);s.connect(('8.8.8.8',80));print(s.getsockname()[0]);s.close()" 2^>nul') do set IP=%%i
if not defined IP (
  for /f "tokens=2 delims=:" %%a in ('%SystemRoot%\System32\ipconfig.exe ^| %SystemRoot%\System32\findstr.exe /c:"IPv4"') do (
    if not defined IP (
      for /f "tokens=* delims= " %%b in ("%%a") do (
        echo %%b | %SystemRoot%\System32\findstr.exe /r /b "127\. 169\.254\. 192\.168\.56\. 192\.168\.116\. 192\.168\.153\." >nul
        if errorlevel 1 set IP=%%b
      )
    )
  )
)
if not defined IP set IP=YOUR-PC-IP

echo.
echo  ========================================
echo   OPEN ON THIS PC:
echo   http://localhost:%PORT%
echo.
echo   OPEN ON PHONE (same Wi-Fi):
echo   http://%IP%:%PORT%
if "%IP%"=="YOUR-PC-IP" (
  echo.
  echo   Could not auto-detect IP. Run in Command Prompt:
  echo   %SystemRoot%\System32\ipconfig.exe
  echo   Use IPv4 under "Wireless LAN adapter Wi-Fi" ^(not VMware/VirtualBox^)
  echo   Then on iPhone Safari:  http://THAT-IP:%PORT%
)
echo.
echo   INSTALL:
echo   - Android: Chrome menu - Install app
echo   - iPhone: Safari Share - Add to Home Screen
echo   - PC: Chrome/Edge address bar - Install
echo.
echo   PHONE WON'T CONNECT? Run once as Administrator:
echo   allow-phone-access.bat
echo   (Windows Firewall blocks port %PORT% by default)
echo  ========================================
echo.

uvicorn app.main:app --host 0.0.0.0 --port %PORT%
