@echo off
REM HARBOR Diamond Viewer - Portable Setup (No Python Required)
REM Run this as Administrator

echo ========================================
echo HARBOR Diamond Viewer - Portable Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    echo Right-click setup.bat and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/3] Creating recordings directory...
if not exist "recordings" mkdir recordings
echo ✓ Recordings directory created
echo.

echo [2/3] Configuring Windows Firewall...
netsh advfirewall firewall delete rule name="HARBOR Diamond Viewer" >nul 2>&1
netsh advfirewall firewall add rule name="HARBOR Diamond Viewer" dir=in action=allow protocol=TCP localport=5000
echo ✓ Firewall configured (Port 5000 allowed)
echo.

echo [3/3] Setting up auto-start (Task Scheduler)...

REM Get current directory
set "CURRENT_DIR=%cd%"

REM Delete old tasks (in case they existed)
schtasks /Delete /TN "HARBOR_DiamondViewer" /F >nul 2>&1
schtasks /Delete /TN "HARBOR_DisplayViewer" /F >nul 2>&1
schtasks /Delete /TN "HARBOR_WebServer" /F >nul 2>&1

REM Create auto-start task
schtasks /Create /TN "HARBOR_DiamondViewer" /TR "\"%CURRENT_DIR%\HARBOR_DiamondViewer.exe\"" /SC ONLOGON /RL HIGHEST /F
if %errorLevel% neq 0 (
    echo WARNING: Failed to create auto-start task
) else (
    echo ✓ Auto-start configured
)
echo.

echo Starting application...
start "" "%CURRENT_DIR%\HARBOR_DiamondViewer.exe"
echo ✓ Application started
echo.

echo ========================================
echo Setup Complete! ✓
echo ========================================
echo.
echo Next steps:
echo 1. Upload Arduino firmware using Arduino IDE
echo    - Open: src/LattePanda_Diamond_Viewer.ino
echo    - Board: Arduino Leonardo
echo    - Click Upload
echo.
echo 2. Test the system:
echo    - Application should be running fullscreen
echo    - Web server runs automatically in background
echo    - Scan QR code from your phone
echo.
echo 3. System will auto-start on next boot
echo.
echo No Python installation required! ✓
echo.
pause
