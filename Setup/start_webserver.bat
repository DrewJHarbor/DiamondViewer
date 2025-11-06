@echo off
REM HARBOR Diamond Viewer - Web Server Launcher
REM Auto-starts the Flask web server for mobile control

cd /d "%~dp0"

echo Starting HARBOR Web Server...
python web_server.py

REM Keep window open if error occurs
if %errorLevel% neq 0 (
    echo.
    echo ERROR: Web server failed to start
    echo Check the error message above
    pause
)
