@echo off
REM HARBOR Diamond Viewer - Build Executable
REM Creates standalone .exe file that includes Python + all dependencies

echo ========================================
echo HARBOR Diamond Viewer - Build Executable
echo ========================================
echo.

echo [1/4] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)
echo ✓ PyInstaller ready
echo.

echo [2/4] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec
echo ✓ Cleaned
echo.

echo [3/4] Building executable (this may take 2-3 minutes)...
pyinstaller --onefile ^
    --windowed ^
    --name="HARBOR_DiamondViewer" ^
    --icon=NONE ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --hidden-import=engineio.async_drivers.threading ^
    --hidden-import=eventlet ^
    --hidden-import=eventlet.wsgi ^
    --hidden-import=dns.resolver ^
    --hidden-import=dns.asyncresolver ^
    --hidden-import=resend ^
    --hidden-import=twilio ^
    --collect-all=flask ^
    --collect-all=flask_socketio ^
    --collect-all=flask_cors ^
    display_viewer.py

if %errorLevel% neq 0 (
    echo.
    echo ❌ Build failed! Check error messages above.
    pause
    exit /b 1
)
echo ✓ Build complete
echo.

echo [4/4] Creating deployment package...
if not exist "DiamondViewer_Portable" mkdir DiamondViewer_Portable
copy /y "dist\HARBOR_DiamondViewer.exe" "DiamondViewer_Portable\"
if not exist "DiamondViewer_Portable\src" mkdir "DiamondViewer_Portable\src"
copy /y "src\LattePanda_Diamond_Viewer.ino" "DiamondViewer_Portable\src\"
copy /y "setup_portable.bat" "DiamondViewer_Portable\setup.bat"
xcopy /E /I /Y "templates" "DiamondViewer_Portable\templates"
xcopy /E /I /Y "static" "DiamondViewer_Portable\static"
if not exist "DiamondViewer_Portable\recordings" mkdir "DiamondViewer_Portable\recordings"

echo ✓ Portable package created
echo.

echo ========================================
echo Build Complete! ✓
echo ========================================
echo.
echo Output: DiamondViewer_Portable\
echo   - HARBOR_DiamondViewer.exe (standalone, no Python needed)
echo   - setup.bat (configures auto-start)
echo   - Arduino firmware
echo   - Web templates
echo.
echo File size: ~60-80 MB (includes Python + all libraries)
echo.
echo Next steps:
echo 1. Copy "DiamondViewer_Portable" folder to USB drive
echo 2. On LattePanda, run setup.bat as administrator
echo 3. Upload Arduino firmware
echo 4. Done! No Python installation required.
echo.
pause
