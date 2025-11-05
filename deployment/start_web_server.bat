@echo off
REM HARBOR Diamond Viewer - Web Server Startup Script
REM This script launches the Flask web server for mobile control
REM Run as Administrator for best results

cd /d %~dp0..
python web_server.py

REM If server crashes, wait and restart
timeout /t 5
goto :eof
