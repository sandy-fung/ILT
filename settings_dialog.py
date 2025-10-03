import tkinter as tk
from tkinter import ttk, messagebox
from log_levels import DEBUG, INFO, ERROR
from hotkey_capture import HotkeyCapture
from config_utils import get_all_hotkeys, get_default_hotkeys, get_hotkey_action_name

DEFAULT_LABEL_FONT_SIZE = 10
DIALOG_WIDTH = 550
DIALOG_HEIGHT = 600
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
        self.show_cut_image_var = tk.BooleanVar()
        self.show_bbox_dimensions_var = tk.BooleanVar()
        self.label_font_size_current = str(DEFAULT_LABEL_FONT_SIZE)  # Default font size

        # Hotkey settings
        self.hotkey_captures = {}  # Store HotkeyCapture widgets
        self.current_hotkeys = {}  # Store current hotkey mappings

        self.create_dialog()

    def create_dialog(self):
        """Create the settings dialog UI"""
        try:
            # Create toplevel window with fixed size
            self.dialog = tk.Toplevel(self.parent)
            self.dialog.title("Configuration")
            self.dialog.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}")
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
        from ILT_UI import DEFAULT_MIN_PLATE_WIDTH
        """Load current settings into dialog variables"""
        try:
            self.show_class_id_buttons_var.set(self.current_settings.get('show_class_id_buttons', False))
            self.show_text_box_var.set(self.current_settings.get('show_text_box', True))
            self.show_preview_var.set(self.current_settings.get('show_preview', True))
            self.show_input_box_var.set(self.current_settings.get('show_input_box', True))
            self.show_classify_frame_var.set(self.current_settings.get('show_classify_frame', True))
            self.show_cut_image_var.set(self.current_settings.get('show_cut_image', True))
            self.show_bbox_dimensions_var.set(self.current_settings.get('show_bbox_dimensions', False))
            self.label_font_size_current = self.current_settings.get('label_font_size')
            self.min_bbox_width_threshold = self.current_settings.get('min_bbox_width_threshold', DEFAULT_MIN_PLATE_WIDTH)

            # Load hotkey settings
            self.current_hotkeys = get_all_hotkeys()

            DEBUG("Loaded current settings into dialog")

        except Exception as e:
            ERROR("Error loading current settings: {}", e)

    def create_ui_elements(self):
        from ILT_UI import DEFAULT_MIN_PLATE_WIDTH
        """Create dialog UI elements"""
        try:
            # Main frame with smaller padding
            main_frame = ttk.Frame(self.dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Create notebook for tabs
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Bind tab change event to prevent auto-focus
            self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

            # Create tabs
            self.create_ui_settings_tab()
            self.create_hotkey_settings_tab()

            # Button frame at bottom
            self.create_button_frame(main_frame)

            DEBUG("UI elements created successfully")

        except Exception as e:
            ERROR("Error creating UI elements: {}", e)

    def create_ui_settings_tab(self):
        """Create UI settings tab"""
        from ILT_UI import DEFAULT_MIN_PLATE_WIDTH

        # Create tab frame
        ui_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(ui_tab, text="UI Settings")

        # Settings frame with minimal padding
        settings_frame = ttk.LabelFrame(ui_tab, text="Display Options", padding="10")
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

        checkbox6 = ttk.Checkbutton(
            settings_frame,
            text="Show Cut Image Button",
            variable=self.show_cut_image_var
        )
        checkbox6.pack(anchor=tk.W, pady=2)

        checkbox7 = ttk.Checkbutton(
            settings_frame,
            text="Show Bbox Dimensions",
            variable=self.show_bbox_dimensions_var
        )
        checkbox7.pack(anchor=tk.W, pady=2)

        # font size for label ascci
        font_frame = ttk.LabelFrame(ui_tab, text="", padding="10")
        font_frame.pack(fill=tk.X, pady=(0, 10))
        font_describe = tk.Label(font_frame, text="label text size", font=("Arial", 11))
        font_describe.grid(row=0, column=0, padx=5, pady=10)
        size = self.current_settings.get('label_font_size')
        self.label_font_size_entry = tk.Entry(font_frame, font=("Arial", 12))
        self.label_font_size_entry.grid(row=0, column=1, padx=5, pady=10)
        self.label_font_size_entry.insert(0, str(size))
        self.label_font_size_entry.config(fg="gray")

        # Minimum bbox width threshold
        threshold_describe = tk.Label(font_frame, text="Min bbox width (pixels)", font=("Arial", 11))
        threshold_describe.grid(row=1, column=0, padx=5, pady=10)
        threshold_value = self.current_settings.get('min_bbox_width_threshold', DEFAULT_MIN_PLATE_WIDTH)
        self.min_bbox_width_entry = tk.Entry(font_frame, font=("Arial", 12))
        self.min_bbox_width_entry.grid(row=1, column=1, padx=5, pady=10)
        self.min_bbox_width_entry.insert(0, str(threshold_value))
        self.min_bbox_width_entry.config(fg="gray")

    def create_hotkey_settings_tab(self):
        """Create hotkey settings tab"""
        hotkey_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(hotkey_tab, text="Hotkeys")

        # Create scrollable frame
        canvas = tk.Canvas(hotkey_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(hotkey_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Info label
        info_label = ttk.Label(
            scrollable_frame,
            text="Click on a hotkey field and press the desired key combination",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        info_label.pack(pady=(0, 10))

        # Create hotkey configuration frame
        hotkeys_frame = ttk.LabelFrame(scrollable_frame, text="Hotkey Bindings", padding="10")
        hotkeys_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create hotkey capture widgets for each action
        for action_key, hotkey in self.current_hotkeys.items():
            action_name = get_hotkey_action_name(action_key)

            # Create row frame
            row_frame = ttk.Frame(hotkeys_frame)
            row_frame.pack(fill=tk.X, pady=5)

            # Action label
            label = ttk.Label(row_frame, text=action_name, width=30, anchor='w')
            label.pack(side=tk.LEFT, padx=(0, 10))

            # Hotkey capture widget
            capture = HotkeyCapture(
                row_frame,
                initial_hotkey=hotkey,
                on_change=lambda h, a=action_key: self.on_hotkey_change(a, h)
            )
            capture.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Store reference
            self.hotkey_captures[action_key] = capture

        # Reset button
        reset_frame = ttk.Frame(scrollable_frame)
        reset_frame.pack(fill=tk.X, pady=(10, 0))

        reset_btn = ttk.Button(
            reset_frame,
            text="Reset to Defaults",
            command=self.reset_hotkeys
        )
        reset_btn.pack(side=tk.RIGHT)

        # Pack scrollable elements
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Ensure no entry has focus when tab is created
        hotkey_tab.focus_set()

    def on_hotkey_change(self, action_key, new_hotkey):
        """Handle hotkey change and check for conflicts"""
        # Update current hotkeys
        old_hotkey = self.current_hotkeys.get(action_key)
        self.current_hotkeys[action_key] = new_hotkey

        # Check for conflicts
        conflicts = []
        for other_action, other_hotkey in self.current_hotkeys.items():
            if other_action != action_key and other_hotkey == new_hotkey and new_hotkey:
                conflicts.append(get_hotkey_action_name(other_action))

        if conflicts:
            # Show warning
            conflict_msg = f"Warning: This hotkey is already used by:\n" + "\n".join(f"- {c}" for c in conflicts)
            messagebox.showwarning("Hotkey Conflict", conflict_msg, parent=self.dialog)

            # Revert to old hotkey
            self.current_hotkeys[action_key] = old_hotkey
            self.hotkey_captures[action_key].set_hotkey(old_hotkey)

        DEBUG("Hotkey for {} changed to {}", action_key, new_hotkey)

    def reset_hotkeys(self):
        """Reset all hotkeys to default values"""
        try:
            default_hotkeys = get_default_hotkeys()

            for action_key, hotkey in default_hotkeys.items():
                self.current_hotkeys[action_key] = hotkey
                if action_key in self.hotkey_captures:
                    self.hotkey_captures[action_key].set_hotkey(hotkey)

            INFO("Hotkeys reset to defaults")

        except Exception as e:
            ERROR("Error resetting hotkeys: {}", e)

    def _on_tab_changed(self, event):
        """Handle notebook tab change to prevent auto-focus on hotkey entries"""
        # Get current tab
        current_tab = self.notebook.select()
        # Get the tab widget
        tab_widget = self.notebook.nametowidget(current_tab)
        # Set focus to the tab itself instead of any child widget
        tab_widget.focus_set()

    def create_button_frame(self, parent):
        """Create button frame with Save and Cancel buttons"""
        # Button frame
        button_frame = ttk.Frame(parent)
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

    def get_settings(self):
        """Get current settings from dialog"""
        return {
            'show_class_id_buttons': self.show_class_id_buttons_var.get(),
            'show_text_box': self.show_text_box_var.get(),
            'show_preview': self.show_preview_var.get(),
            'show_input_box': self.show_input_box_var.get(),
            'show_classify_frame': self.show_classify_frame_var.get(),
            'show_cut_image': self.show_cut_image_var.get(),
            'show_bbox_dimensions': self.show_bbox_dimensions_var.get(),
            'label_font_size': int(self.label_font_size_entry.get()),
            'min_bbox_width_threshold': int(self.min_bbox_width_entry.get()),
            'hotkeys': self.current_hotkeys.copy()
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
    from ILT_UI import DEFAULT_MIN_PLATE_WIDTH
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
        'show_cut_image': True,
        'show_bbox_dimensions': False,
        'label_font_size_entry': 12,
        'min_bbox_width_threshold': DEFAULT_MIN_PLATE_WIDTH
    }

    dialog = SettingsDialog(parent_window, current_settings, on_confirm)
    try:
        dialog.show()
        print("Dialog shown")
    except Exception as e:
        print(f"Error: {e}")

    # Destroy the temporary parent window after the dialog is closed
    parent_window.destroy()
