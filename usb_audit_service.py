"""
USB Drive Audit Logger Service
Logs access information directly to external USB drives only
Ignores internal hard drives and fixed disks
Designed for IT security and audit compliance
"""

import os
import sys
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from datetime import datetime
import string
from ctypes import windll
import json
import win32api

class USBDriveAuditLogger(win32serviceutil.ServiceFramework):
    _svc_name_ = "WindowsUpdateHelperService"
    _svc_display_name_ = "Windows Update Helper Service"
    _svc_description_ = "Provides auxiliary support for Windows Update operations"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        socket.setdefaulttimeout(60)
        
        # Store initial system drives to ignore them
        self.system_drives = set()
        self.initialize_system_drives()

    def initialize_system_drives(self):
        """
        Store ONLY fixed/internal drives (Type 3) that exist at service startup
        Removable drives (Type 2) will ALWAYS be monitored, even if present at startup
        """
        try:
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                    # ONLY store Type 3 (fixed/internal hard drives) to ignore
                    # Type 2 (removable) will always be monitored
                    if drive_type == 3:  # DRIVE_FIXED only
                        self.system_drives.add(letter)
            
            servicemanager.LogInfoMsg(f"Fixed system drives (will be ignored): {', '.join(sorted(self.system_drives)) if self.system_drives else 'None'}")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error identifying system drives: {str(e)}")

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def get_current_user(self):
        """Get currently logged in user"""
        try:
            return win32api.GetUserName()
        except:
            return "SYSTEM"

    def get_computer_name(self):
        """Get computer name"""
        try:
            return win32api.GetComputerName()
        except:
            return "UNKNOWN"

    def get_available_drives(self):
        """Get list of all available drive letters"""
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1
        return drives

    def is_external_removable_drive(self, drive):
        """
        Check if drive is an external removable drive (USB, external HDD, etc.)
        Returns True for ANY Type 2 (removable) drive, regardless of when it was plugged in
        Only ignores Type 3 (fixed/internal) drives
        """
        try:
            # Check if it's a fixed system drive (like C:)
            if drive in self.system_drives:
                return False
            
            drive_path = f"{drive}:\\"
            
            # Check if path exists
            if not os.path.exists(drive_path):
                return False
            
            # Get drive type
            drive_type = windll.kernel32.GetDriveTypeW(drive_path)
            
            # Type 2 = DRIVE_REMOVABLE (USB drives, memory cards, external HDDs, etc.)
            # We want ALL Type 2 drives, even if they were present at startup
            if drive_type == 2:
                return True
            
            return False
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error checking drive {drive}: {str(e)}")
            return False

    def get_drive_info(self, drive):
        """Get detailed drive information"""
        try:
            drive_path = f"{drive}:\\"
            
            # Get volume information
            volume_info = win32api.GetVolumeInformation(drive_path)
            volume_name = volume_info[0]
            serial_number = volume_info[1]
            
            # Get drive size
            try:
                free_bytes, total_bytes, total_free = win32api.GetDiskFreeSpaceEx(drive_path)
                size_gb = total_bytes / (1024**3)
                free_gb = free_bytes / (1024**3)
            except:
                size_gb = 0
                free_gb = 0
            
            # Get drive type name
            drive_type = windll.kernel32.GetDriveTypeW(drive_path)
            type_names = {
                0: "Unknown",
                1: "No Root Directory",
                2: "Removable",
                3: "Fixed",
                4: "Network",
                5: "CD-ROM",
                6: "RAM Disk"
            }
            drive_type_name = type_names.get(drive_type, "Unknown")
            
            return {
                'volume_name': volume_name if volume_name else 'Unnamed',
                'serial_number': hex(serial_number) if serial_number else 'N/A',
                'size_gb': round(size_gb, 2),
                'free_gb': round(free_gb, 2),
                'drive_type': drive_type_name
            }
        except Exception as e:
            return {
                'volume_name': 'Unknown',
                'serial_number': 'N/A',
                'size_gb': 0,
                'free_gb': 0,
                'drive_type': 'Unknown',
                'error': str(e)
            }

    def create_audit_files(self, drive):
        """Create audit log files on the USB drive"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user = self.get_current_user()
            computer = self.get_computer_name()
            drive_info = self.get_drive_info(drive)
            
            # Create visible info.txt file
            info_path = f"{drive}:\\info.txt"
            info_content = f"""USB Storage Device Access Log
{'='*50}

Timestamp: {timestamp}
User: {user}
Computer: {computer}
Drive Letter: {drive}:
Volume Name: {drive_info['volume_name']}
Serial Number: {drive_info['serial_number']}
Drive Type: {drive_info['drive_type']}
Total Size: {drive_info['size_gb']} GB
Free Space: {drive_info['free_gb']} GB

{'='*50}
This device was accessed on the above system.
For security purposes, all access is logged.
"""
            
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(info_content)
            
            # Create/update hidden detailed log
            hidden_log_path = f"{drive}:\\.access_audit.log"
            
            # Read existing log entries
            log_entries = []
            if os.path.exists(hidden_log_path):
                try:
                    with open(hidden_log_path, 'r', encoding='utf-8') as f:
                        log_entries = json.load(f)
                except:
                    log_entries = []
            
            # Add new entry
            new_entry = {
                'timestamp': timestamp,
                'user': user,
                'computer': computer,
                'drive_letter': f"{drive}:",
                'volume_name': drive_info['volume_name'],
                'serial_number': drive_info['serial_number'],
                'drive_type': drive_info['drive_type'],
                'size_gb': drive_info['size_gb'],
                'free_gb': drive_info['free_gb']
            }
            
            log_entries.append(new_entry)
            
            # Write updated log
            with open(hidden_log_path, 'w', encoding='utf-8') as f:
                json.dump(log_entries, f, indent=2)
            
            # Hide the detailed log file
            try:
                windll.kernel32.SetFileAttributesW(hidden_log_path, 0x02)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
            
            # Create audit summary file
            summary_path = f"{drive}:\\access_history.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("USB Drive Access History\n")
                f.write("="*60 + "\n\n")
                
                for idx, entry in enumerate(log_entries, 1):
                    f.write(f"Access #{idx}\n")
                    f.write(f"  Date/Time: {entry['timestamp']}\n")
                    f.write(f"  User: {entry['user']}\n")
                    f.write(f"  Computer: {entry['computer']}\n")
                    f.write(f"  Drive: {entry['drive_letter']}\n")
                    f.write(f"  Type: {entry.get('drive_type', 'N/A')}\n")
                    f.write("-" * 60 + "\n")
                
                f.write(f"\nTotal Access Count: {len(log_entries)}\n")
                f.write(f"First Access: {log_entries[0]['timestamp'] if log_entries else 'N/A'}\n")
                f.write(f"Last Access: {log_entries[-1]['timestamp'] if log_entries else 'N/A'}\n")
            
            log_msg = f"Created audit files on external drive {drive}: for user {user}"
            servicemanager.LogInfoMsg(log_msg)
            return True
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error creating audit files on {drive}: {str(e)}")
            return False

    def main(self):
        """Main monitoring loop"""
        # Get initial drives (only external/removable ones)
        previous_drives = set()
        for drive in self.get_available_drives():
            if self.is_external_removable_drive(drive):
                previous_drives.add(drive)
        
        servicemanager.LogInfoMsg(f"USB Drive Audit Logger started. Monitoring ALL removable drives.")
        servicemanager.LogInfoMsg(f"Fixed drives (ignored): {', '.join(sorted(self.system_drives)) if self.system_drives else 'None'}")
        if previous_drives:
            servicemanager.LogInfoMsg(f"Removable drives already connected: {', '.join(sorted(previous_drives))}")
        
        while self.running:
            try:
                # Get current external/removable drives
                current_drives = set()
                for drive in self.get_available_drives():
                    if self.is_external_removable_drive(drive):
                        current_drives.add(drive)
                
                # Detect new external drives
                new_drives = current_drives - previous_drives
                for drive in new_drives:
                    servicemanager.LogInfoMsg(f"New external USB drive detected: {drive}:")
                    # Wait for drive to be fully ready
                    time.sleep(2)
                    self.create_audit_files(drive)
                
                # Detect removed drives (for logging purposes)
                removed_drives = previous_drives - current_drives
                for drive in removed_drives:
                    servicemanager.LogInfoMsg(f"External USB drive removed: {drive}:")
                
                previous_drives = current_drives
                
                # Check every 2 seconds
                if win32event.WaitForSingleObject(self.stop_event, 2000) == win32event.WAIT_OBJECT_0:
                    break
                    
            except Exception as e:
                servicemanager.LogErrorMsg(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)
        
        servicemanager.LogInfoMsg("USB Drive Audit Logger stopped")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(USBDriveAuditLogger)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(USBDriveAuditLogger)