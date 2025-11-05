@echo off
REM HARBOR Diamond Viewer - Display Startup Script
REM This script launches the fullscreen display viewer on Windows boot
REM Place this in Windows Startup folder: shell:startup

cd /d %~dp0..
python display_viewer.py

REM If display crashes, wait and restart
timeout /t 5
goto :eof
