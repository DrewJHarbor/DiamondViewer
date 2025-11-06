@echo off
REM HARBOR Diamond Viewer - Automated Setup Script
REM Run this as Administrator on fresh LattePanda installation

echo ========================================
echo HARBOR Diamond Viewer - Setup
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

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found! Please install Python first.
    echo Download from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo.

echo [2/6] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo [3/6] Creating recordings directory...
if not exist "recordings" mkdir recordings
echo ✓ Recordings directory created
echo.

echo [4/6] Configuring Windows Firewall...
netsh advfirewall firewall delete rule name="HARBOR Diamond Viewer" >nul 2>&1
netsh advfirewall firewall add rule name="HARBOR Diamond Viewer" dir=in action=allow protocol=TCP localport=5000
echo ✓ Firewall configured (Port 5000 allowed)
echo.

echo [5/6] Setting up auto-start (Task Scheduler)...

REM Get current directory
set "CURRENT_DIR=%cd%"

REM Create task for Display Viewer
schtasks /Delete /TN "HARBOR_DisplayViewer" /F >nul 2>&1
schtasks /Create /TN "HARBOR_DisplayViewer" /TR "\"%CURRENT_DIR%\start_display.bat\"" /SC ONLOGON /RL HIGHEST /F
if %errorLevel% neq 0 (
    echo WARNING: Failed to create Display Viewer auto-start task
) else (
    echo ✓ Display Viewer auto-start configured
)

REM Create task for Web Server
schtasks /Delete /TN "HARBOR_WebServer" /F >nul 2>&1
schtasks /Create /TN "HARBOR_WebServer" /TR "\"%CURRENT_DIR%\start_webserver.bat\"" /SC ONLOGON /RL HIGHEST /F
if %errorLevel% neq 0 (
    echo WARNING: Failed to create Web Server auto-start task
) else (
    echo ✓ Web Server auto-start configured
)
echo.

echo [6/6] Starting applications...
start "HARBOR Display Viewer" /MIN cmd /c "%CURRENT_DIR%\start_display.bat"
timeout /t 3 /nobreak >nul
start "HARBOR Web Server" /MIN cmd /c "%CURRENT_DIR%\start_webserver.bat"
echo ✓ Applications started
echo.

echo ========================================
echo Setup Complete! ✓
echo ========================================
echo.
echo Next steps:
echo 1. Upload Arduino firmware using Arduino IDE
echo    - Open: LattePanda_Diamond_Viewer.ino
echo    - Board: Arduino Leonardo
echo    - Click Upload
echo.
echo 2. Test the system:
echo    - Display Viewer should be running fullscreen
echo    - Scan QR code from your phone
echo    - Control motors from mobile interface
echo.
echo 3. The system will auto-start on next boot
echo.
echo For troubleshooting, see DEPLOYMENT_GUIDE.md
echo.
pause
