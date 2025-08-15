import tkinter as tk
from tkinter import ttk
from log_levels import DEBUG, INFO, ERROR

DEFAULT_LABEL_FONT_SIZE = 10
DIALOG_WIDTH = 400
DIALOG_HEIGHT = 360
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
        self.show_classify_frame_var = tk.BooleanVar()
        self.label_font_size_current = str(DEFAULT_LABEL_FONT_SIZE)  # Default font size

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
            dialog_width = DIALOG_WIDTH
            dialog_height = DIALOG_HEIGHT

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
            self.show_classify_frame_var.set(self.current_settings.get('show_classify_frame', True))
            self.label_font_size_current = self.current_settings.get('label_font_size')



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
            
            checkbox5 = ttk.Checkbutton(
                settings_frame,
                text="Show classification panel",
                variable=self.show_classify_frame_var
            )
            checkbox5.pack(anchor=tk.W, pady=2)
            
            # font size for label ascci
            font_frame = ttk.LabelFrame(main_frame, text="", padding="10")
            font_frame.pack(fill=tk.X, pady=(0, 10))
            font_describe = tk.Label(font_frame, text="label text size", font=("Arial", 11))
            font_describe.grid(row=0, column=0, padx=5, pady=10)
            size = self.current_settings.get('label_font_size')
            self.label_font_size_entry = tk.Entry(font_frame, font=("Arial", 12))
            self.label_font_size_entry.grid(row=0, column=1, padx=5, pady=10)
            self.label_font_size_entry.insert(0, str(size))
            self.label_font_size_entry.config(fg="gray")

            # self.label_font_size_entry.delete(0, tk.END)
            # size =  self.current_settings.get('label_font_size', DEFAULT_LABEL_FONT_SIZE)
            # self.label_font_size_entry.insert(0, str(size))
            # self.label_font_size_entry.config(fg="gray")

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
            'show_input_box': self.show_input_box_var.get(),
            'show_classify_frame': self.show_classify_frame_var.get(),
            'label_font_size': int(self.label_font_size_entry.get())
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


# for implementation testing
if __name__ == "__main__":
    def on_confirm(settings):
        print("Settings confirmed:", settings)

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    parent_window = tk.Toplevel(root)
    parent_window.title("Temporary Parent")
    parent_window.geometry("300x200")  # Set size for the parent window

    current_settings = {
        'show_class_id_buttons': True,
        'show_text_box': True,
        'show_preview': True,
        'show_input_box': True,
        'show_classify_frame': True,
        'label_font_size_entry': 12
    }

    dialog = SettingsDialog(parent_window, current_settings, on_confirm)
    try:
        dialog.show()
        print("Dialog shown")
    except Exception as e:
        print(f"Error: {e}")

    # Destroy the temporary parent window after the dialog is closed
    parent_window.destroy()
