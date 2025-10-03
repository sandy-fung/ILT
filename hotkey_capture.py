import tkinter as tk
from tkinter import ttk

class HotkeyCapture(ttk.Frame):
    """Widget for capturing and displaying keyboard shortcuts"""

    def __init__(self, parent, initial_hotkey='', on_change=None, **kwargs):
        """
        Initialize hotkey capture widget

        Args:
            parent: Parent widget
            initial_hotkey: Initial hotkey in Tkinter format (e.g., '<Control-f>')
            on_change: Callback function when hotkey changes
        """
        super().__init__(parent, **kwargs)

        self.current_hotkey = initial_hotkey
        self.on_change = on_change

        # Track actually pressed modifier keys to avoid false Alt detection
        self.pressed_modifiers = set()

        # Create container frame for entry and clear button
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Create entry widget
        self.entry = ttk.Entry(container, width=20, justify='center')
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create clear button
        self.clear_btn = ttk.Button(container, text="✕", width=3, command=self._on_clear)
        self.clear_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Display initial hotkey
        self.update_display()

        # Bind events
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)

        # Use KeyPress for capturing - it fires before text is inserted
        self.entry.bind('<KeyPress>', self._on_key_press)

        # Track modifier key states to avoid false Alt detection
        self.entry.bind('<KeyPress>', self._track_modifier_press, add='+')
        self.entry.bind('<KeyRelease>', self._track_modifier_release, add='+')

    def _track_modifier_press(self, event):
        """Track when modifier keys are actually pressed"""
        if event.keysym in ['Alt_L', 'Alt_R', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R']:
            self.pressed_modifiers.add(event.keysym)

    def _track_modifier_release(self, event):
        """Track when modifier keys are actually released"""
        if event.keysym in ['Alt_L', 'Alt_R', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R']:
            self.pressed_modifiers.discard(event.keysym)

    def _on_focus_in(self, event):
        """Handle focus in - show capture prompt"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "Press any key...")
        self.entry.config(foreground='gray')
        # Clear modifier tracking when focus changes
        self.pressed_modifiers.clear()

    def _on_focus_out(self, event):
        """Handle focus out - restore hotkey display"""
        self.update_display()
        # Clear modifier tracking when focus changes
        self.pressed_modifiers.clear()

    def _on_clear(self):
        """Handle clear button click - remove hotkey"""
        self.current_hotkey = ''
        self.update_display()

        # Call change callback
        if self.on_change:
            self.on_change(self.current_hotkey)

    def _on_key_press(self, event):
        """Capture key press event and convert to hotkey format"""
        # Allow Tab key for navigation
        if event.keysym == 'Tab':
            return  # Let Tab work normally for navigation

        # Build hotkey string from event
        modifiers = []

        # Check for modifier keys
        if event.state & 0x0001:  # Shift
            modifiers.append('Shift')
        if event.state & 0x0004:  # Control
            modifiers.append('Control')
        # Use actual key tracking for Alt to avoid false positives from event.state
        if 'Alt_L' in self.pressed_modifiers or 'Alt_R' in self.pressed_modifiers:
            modifiers.append('Alt')

        # Get the key symbol
        key = event.keysym

        # Skip if only modifier key is pressed
        if key in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            # Allow certain modifiers as standalone hotkeys
            if key in ['Control_L', 'Shift_L', 'Shift_R'] and not modifiers:
                self.current_hotkey = f'<{key}>'
                self.update_display()
                if self.on_change:
                    self.on_change(self.current_hotkey)
                return 'break'
            return 'break'

        # Handle special keys that shouldn't have modifiers removed
        if key in ['Left', 'Right', 'Up', 'Down', 'Delete', 'BackSpace',
                   'Return', 'Escape', 'space']:
            # For arrow keys and special keys, don't use modifiers unless explicitly pressed
            if not modifiers:
                self.current_hotkey = f'<{key}>'
            else:
                self.current_hotkey = f"<{'-'.join(modifiers)}-{key}>"
        else:
            # For regular keys (letters, numbers)
            if modifiers:
                # If there are modifiers, use them
                self.current_hotkey = f"<{'-'.join(modifiers)}-{key}>"
            else:
                # For single letter keys without modifiers, use lowercase
                # Special handling for lowercase keys
                if len(key) == 1 and key.isalpha():
                    self.current_hotkey = f'<{key.lower()}>'
                else:
                    self.current_hotkey = f'<{key}>'

        # Update display immediately
        self.update_display()

        # Call change callback
        if self.on_change:
            self.on_change(self.current_hotkey)

        # Prevent default handling (text insertion)
        return 'break'

    def update_display(self):
        """Update entry display with friendly hotkey name"""
        friendly_name = self.get_friendly_name(self.current_hotkey)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, friendly_name)
        self.entry.config(foreground='black')

    def get_friendly_name(self, hotkey):
        """Convert Tkinter hotkey format to friendly display name"""
        if not hotkey:
            return 'Not set'

        # Remove angle brackets
        hotkey = hotkey.strip('<>')

        # Replace key names with friendly names
        replacements = {
            'Control': 'Ctrl',
            'Control_L': 'Left Ctrl',
            'Control_R': 'Right Ctrl',
            'Shift': 'Shift',
            'Alt': 'Alt',
            'Left': '←',
            'Right': '→',
            'Up': '↑',
            'Down': '↓',
            'Delete': 'Del',
            'BackSpace': 'Backspace',
            'Return': 'Enter',
            'Escape': 'Esc',
            'space': 'Space',
        }

        # Split by dash and replace each part
        parts = hotkey.split('-')
        friendly_parts = []

        for part in parts:
            friendly_parts.append(replacements.get(part, part.upper() if len(part) == 1 else part))

        return '+'.join(friendly_parts)

    def get_hotkey(self):
        """Get current hotkey in Tkinter format"""
        return self.current_hotkey

    def set_hotkey(self, hotkey):
        """Set hotkey programmatically"""
        self.current_hotkey = hotkey
        self.update_display()


# Test code
if __name__ == '__main__':
    def on_hotkey_change(hotkey):
        print(f"Hotkey changed to: {hotkey}")

    root = tk.Tk()
    root.title("Hotkey Capture Test")
    root.geometry("300x200")

    label = ttk.Label(root, text="Click and press a key combination:")
    label.pack(pady=10)

    capture = HotkeyCapture(root, initial_hotkey='<Control-f>', on_change=on_hotkey_change)
    capture.pack(pady=10, padx=20, fill=tk.X)

    # Test button to get current hotkey
    def show_hotkey():
        print(f"Current hotkey: {capture.get_hotkey()}")

    btn = ttk.Button(root, text="Show Hotkey", command=show_hotkey)
    btn.pack(pady=10)

    root.mainloop()
