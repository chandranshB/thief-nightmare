@echo off
REM ============================================================================
REM USB File Overwriter - Configuration Utility
REM Easy way to change file filtering modes
REM ============================================================================

setlocal enabledelayedexpansion

echo ============================================================================
echo USB File Overwriter - Configuration Utility
echo ============================================================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator!
    echo You may need Administrator privileges to restart the service.
    echo.
    echo For full functionality, right-click and select "Run as Administrator"
    echo.
    pause
)

REM Get the directory where this batch file is located
set "BATCH_DIR=%~dp0"
cd /d "%BATCH_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Please ensure Python is installed and accessible.
    echo If you used the automated installer, Python should be available.
    echo.
    echo Trying alternative Python locations...
    
    REM Try embedded Python from installation
    set "PYTHON_CMD=%ProgramData%\.system\WindowsUpdateHelper\runtime\python.exe"
    if exist "!PYTHON_CMD!" (
        echo Found embedded Python: !PYTHON_CMD!
        goto :run_config
    )
    
    echo No Python installation found.
    echo Please install Python or use the automated installer.
    pause
    exit /b 1
) else (
    set "PYTHON_CMD=python"
)

:run_config
REM Check if configuration script exists
if not exist "%BATCH_DIR%configure_filter.py" (
    echo ERROR: configure_filter.py not found!
    echo.
    echo Please ensure configure_filter.py is in the same folder as this batch file.
    echo Current folder: %BATCH_DIR%
    pause
    exit /b 1
)

REM Run the configuration utility
echo Running configuration utility...
echo.
"%PYTHON_CMD%" "%BATCH_DIR%configure_filter.py"

echo.
echo Configuration utility finished.
pause
endlocal