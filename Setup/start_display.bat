@echo off
REM HARBOR Diamond Viewer - Display Viewer Launcher
REM Auto-starts the fullscreen display with dual cameras

cd /d "%~dp0"

echo Starting HARBOR Display Viewer...
pythonw display_viewer.py

REM If pythonw fails, try python
if %errorLevel% neq 0 (
    python display_viewer.py
)
