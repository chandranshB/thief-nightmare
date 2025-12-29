@echo off
REM ============================================================================
REM USB Security Service - Controller Launcher
REM Opens the stealth service configuration GUI
REM ============================================================================

setlocal enabledelayedexpansion

echo ============================================================================
echo USB Security Service - Configuration Controller
echo ============================================================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator!
    echo Some service control features may not work properly.
    echo.
    echo For full functionality, right-click and select "Run as Administrator"
    echo.
    timeout /t 2 /nobreak >nul
)

REM Try to find the controller in installation directory first
set "INSTALL_DIR=%ProgramData%\.system\WindowsUpdateHelper"
set "CONTROLLER_FILE=%INSTALL_DIR%\usb_service_controller.py"

if exist "%CONTROLLER_FILE%" (
    echo Found controller in installation directory.
    
    REM Try to use the embedded Python first
    set "PYTHON_CMD=%INSTALL_DIR%\runtime\python.exe"
    if exist "!PYTHON_CMD!" (
        echo Using embedded Python: !PYTHON_CMD!
        goto :run_controller
    )
)

REM Fall back to local directory
set "BATCH_DIR=%~dp0"
cd /d "%BATCH_DIR%"

if exist "%BATCH_DIR%src\usb_service_controller.py" (
    set "CONTROLLER_FILE=%BATCH_DIR%src\usb_service_controller.py"
    echo Found controller in source directory.
) else (
    echo ERROR: Controller not found!
    echo.
    echo Please ensure the USB Security Service is installed, or
    echo run this launcher from the project directory.
    pause
    exit /b 1
)

REM Check for Python installation
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found in PATH. Checking alternative locations...
    
    REM Try common Python installation paths
    for %%P in (
        "%LocalAppData%\Programs\Python\Python311\python.exe"
        "%LocalAppData%\Programs\Python\Python310\python.exe"
        "%LocalAppData%\Programs\Python\Python312\python.exe"
        "%ProgramFiles%\Python311\python.exe"
        "%ProgramFiles%\Python310\python.exe"
        "%ProgramFiles%\Python312\python.exe"
        "%ProgramFiles(x86)%\Python311\python.exe"
        "%ProgramFiles(x86)%\Python310\python.exe"
        "%ProgramFiles(x86)%\Python312\python.exe"
    ) do (
        if exist "%%P" (
            set "PYTHON_CMD=%%P"
            echo Found Python: !PYTHON_CMD!
            goto :run_controller
        )
    )
    
    echo.
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.10+ from python.org
    echo Or run the Install.bat installer first.
    echo.
    pause
    exit /b 1
) else (
    set "PYTHON_CMD=python"
    echo Python found in PATH.
)

:run_controller
echo.
echo Checking dependencies...

REM Check for pywin32
"%PYTHON_CMD%" -c "import win32serviceutil" >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing required dependency: pywin32
    "%PYTHON_CMD%" -m pip install pywin32
    if !errorLevel! neq 0 (
        echo.
        echo ERROR: Failed to install pywin32!
        echo Please run as Administrator or install manually:
        echo   pip install pywin32
        echo.
        pause
        exit /b 1
    )
)

echo Dependencies OK.
echo.
echo Starting USB Security Service Controller...
echo.

REM Launch the controller
"%PYTHON_CMD%" "%CONTROLLER_FILE%"

if %errorLevel% neq 0 (
    echo.
    echo Controller exited with error code: %errorLevel%
    pause
)

endlocal