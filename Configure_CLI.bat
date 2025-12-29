@echo off
REM ============================================================================
REM USB Security Service - Command Line Configuration
REM Quick command-line configuration utility
REM ============================================================================

setlocal enabledelayedexpansion

echo ============================================================================
echo USB Security Service - Command Line Configuration
echo ============================================================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator!
    echo You may need Administrator privileges to restart the service.
    echo.
)

REM Try to find Python in installation directory first
set "INSTALL_DIR=%ProgramData%\.system\WindowsUpdateHelper"
set "CONFIG_UTIL=%INSTALL_DIR%\configure_filter.py"

if exist "%CONFIG_UTIL%" (
    echo Found configuration utility in installation directory.
    
    REM Try to use the embedded Python first
    set "PYTHON_CMD=%INSTALL_DIR%\runtime\python.exe"
    if exist "!PYTHON_CMD!" (
        echo Using embedded Python.
        goto :run_config
    )
)

REM Fall back to local directory
set "BATCH_DIR=%~dp0"
cd /d "%BATCH_DIR%"

if exist "%BATCH_DIR%src\configure_filter.py" (
    set "CONFIG_UTIL=%BATCH_DIR%src\configure_filter.py"
    echo Found configuration utility in source directory.
) else (
    echo ERROR: Configuration utility not found!
    echo.
    echo Please ensure the USB Security Service is installed, or
    echo run this from the project directory.
    pause
    exit /b 1
)

REM Check for Python installation
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python or use the GUI controller instead.
    pause
    exit /b 1
) else (
    set "PYTHON_CMD=python"
)

:run_config
echo.
echo Starting configuration utility...
echo.

REM Run the configuration utility
"%PYTHON_CMD%" "%CONFIG_UTIL%"

echo.
echo Configuration utility finished.
pause
endlocal