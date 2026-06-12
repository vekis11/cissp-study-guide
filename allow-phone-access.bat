@echo off
REM Run as Administrator: allows iPhone/other devices on your Wi-Fi to reach port 8080
echo.
echo  CISSP Study — Allow phone access (Windows Firewall)
echo  =====================================================
echo.

net session >nul 2>&1
if errorlevel 1 (
  echo  ERROR: Right-click this file and choose "Run as administrator"
  echo.
  pause
  exit /b 1
)

C:\Windows\System32\netsh.exe advfirewall firewall delete rule name="CISSP Study 8080" >nul 2>&1
C:\Windows\System32\netsh.exe advfirewall firewall add rule name="CISSP Study 8080" dir=in action=allow protocol=TCP localport=8080 profile=private
C:\Windows\System32\netsh.exe advfirewall firewall add rule name="CISSP Study 8080 Public" dir=in action=allow protocol=TCP localport=8080 profile=public

echo.
echo  Done. Port 8080 is now allowed for private and public networks.
echo.
echo  1. Keep start-app.bat running
echo  2. On iPhone Safari open the URL shown in start-app.bat
echo     (usually http://192.168.4.40:8080 — check Wi-Fi IPv4 if unsure)
echo.
pause
