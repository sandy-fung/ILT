import tkinter as tk
from tkinter import ttk
from log_levels import DEBUG, INFO, ERROR

class SettingsDialog:
    def __init__(self, parent, current_settings, on_confirm_callback):
        """
        Initialize settings dialog
        
        Args:
            parent: Parent window
            current_settings: Dictionary of current UI settings
            on_confirm_callback: Callback function when settings are confirmed
        """
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.on_confirm_callback = on_confirm_callback
        self.result = None
        self.dialog = None
        
        # Setting variables
        self.show_class_id_buttons_var = tk.BooleanVar()
        self.show_text_box_var = tk.BooleanVar()
        self.show_preview_var = tk.BooleanVar()
        self.show_input_box_var = tk.BooleanVar()
        
        self.create_dialog()
        
    def create_dialog(self):
        """Create the settings dialog UI"""
        try:
            # Create toplevel window with fixed size
            self.dialog = tk.Toplevel(self.parent)
            self.dialog.title("Configuration")
            self.dialog.geometry("400x300")
            self.dialog.resizable(False, False)
            
            # Make dialog modal
            self.dialog.transient(self.parent)
            self.dialog.grab_set()
            
            # Load current settings into variables
            self.load_current_settings()
            
            # Create UI elements first
            self.create_ui_elements()
            
            # Update window to ensure proper sizing
            self.dialog.update_idletasks()
            
            # Center the dialog after creating elements
            self.center_dialog()
            
            # Bind keyboard events
            self.dialog.bind('<Return>', lambda e: self.on_confirm())
            self.dialog.bind('<Escape>', lambda e: self.on_cancel())
            
            # Focus on dialog
            self.dialog.focus_set()
            
            DEBUG("Settings dialog created successfully")
            
        except Exception as e:
            ERROR("Error creating settings dialog: {}", e)
            
    def center_dialog(self):
        """Center the dialog over parent window"""
        try:
            # Use fixed dialog size
            dialog_width = 400
            dialog_height = 300
            
            # Get parent window position and size
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            # Calculate center position
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            # Ensure dialog is visible on screen
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            
            # Set position with fixed size - this should maintain 400x300
            self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
            # Force the dialog to maintain the fixed size
            self.dialog.minsize(dialog_width, dialog_height)
            self.dialog.maxsize(dialog_width, dialog_height)
            
            DEBUG("Dialog centered at {}x{}+{}+{}", dialog_width, dialog_height, x, y)
            
        except Exception as e:
            ERROR("Error centering dialog: {}", e)
            
    def load_current_settings(self):
        """Load current settings into dialog variables"""
        try:
            self.show_class_id_buttons_var.set(self.current_settings.get('show_class_id_buttons', False))
            self.show_text_box_var.set(self.current_settings.get('show_text_box', True))
            self.show_preview_var.set(self.current_settings.get('show_preview', True))
            self.show_input_box_var.set(self.current_settings.get('show_input_box', True))
            
            DEBUG("Loaded current settings into dialog")
            
        except Exception as e:
            ERROR("Error loading current settings: {}", e)
            
    def create_ui_elements(self):
        """Create dialog UI elements"""
        try:
            # Main frame with smaller padding
            main_frame = ttk.Frame(self.dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Compact title
            title_label = ttk.Label(
                main_frame, 
                text="UI Configuration",
                font=('Arial', 11, 'bold')
            )
            title_label.pack(anchor=tk.W, pady=(0, 10))
            
            # Settings frame with minimal padding
            settings_frame = ttk.LabelFrame(main_frame, text="Display Options", padding="10")
            settings_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Compact checkboxes
            checkbox1 = ttk.Checkbutton(
                settings_frame,
                text="Show Class ID Buttons (0-9, A-Z)",
                variable=self.show_class_id_buttons_var
            )
            checkbox1.pack(anchor=tk.W, pady=2)
            
            checkbox2 = ttk.Checkbutton(
                settings_frame,
                text="Show Text Box",
                variable=self.show_text_box_var
            )
            checkbox2.pack(anchor=tk.W, pady=2)
            
            checkbox3 = ttk.Checkbutton(
                settings_frame,
                text="Show Preview Panel", 
                variable=self.show_preview_var
            )
            checkbox3.pack(anchor=tk.W, pady=2)
            
            checkbox4 = ttk.Checkbutton(
                settings_frame,
                text="Show Input Box",
                variable=self.show_input_box_var
            )
            checkbox4.pack(anchor=tk.W, pady=2)
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Buttons
            cancel_btn = ttk.Button(
                button_frame, 
                text="Cancel", 
                command=self.on_cancel
            )
            cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
            
            confirm_btn = ttk.Button(
                button_frame, 
                text="Save", 
                command=self.on_confirm
            )
            confirm_btn.pack(side=tk.RIGHT)
            
            # Set default button
            confirm_btn.focus_set()
            
            DEBUG("UI elements created successfully")
            
        except Exception as e:
            ERROR("Error creating UI elements: {}", e)
            
    def get_settings(self):
        """Get current settings from dialog"""
        return {
            'show_class_id_buttons': self.show_class_id_buttons_var.get(),
            'show_text_box': self.show_text_box_var.get(),
            'show_preview': self.show_preview_var.get(),
            'show_input_box': self.show_input_box_var.get()
        }
        
    def on_confirm(self):
        """Handle confirm button click"""
        try:
            # Get final settings
            settings = self.get_settings()
            
            DEBUG("Settings confirmed: {}", settings)
            
            # Call callback
            if self.on_confirm_callback:
                self.on_confirm_callback(settings)
                
            # Close dialog
            self.close_dialog()
            
            INFO("Settings dialog confirmed successfully")
            
        except Exception as e:
            ERROR("Error confirming settings: {}", e)
            
    def on_cancel(self):
        """Handle cancel button click"""
        try:
            DEBUG("Settings dialog cancelled")
            self.close_dialog()
            
        except Exception as e:
            ERROR("Error cancelling dialog: {}", e)
            
    def close_dialog(self):
        """Close the dialog"""
        try:
            if self.dialog:
                self.dialog.grab_release()
                self.dialog.destroy()
                self.dialog = None
                
        except Exception as e:
            ERROR("Error closing dialog: {}", e)
            
    def show(self):
        """Show the dialog and wait for result"""
        try:
            if self.dialog:
                self.dialog.wait_window()
                
        except Exception as e:
            ERROR("Error showing dialog: {}", e)