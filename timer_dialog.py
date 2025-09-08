import tkinter as tk
from tkinter import messagebox
from log_levels import DEBUG, INFO, ERROR

class TimerSetupDialog:
    """Simple dialog to set timer duration before starting"""
    def __init__(self, parent, default_minutes=1):
        self.parent = parent
        self.default_minutes = default_minutes
        self.result = None  # Will store the selected minutes
        
        self.create_dialog()
        
    def create_dialog(self):
        """Create the timer setup dialog UI"""
        # Create toplevel window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Timer")
        self.dialog.geometry("300x140")  # Increased size to fit button
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Game time message
        tk.Label(main_frame, 
                text=f"遊戲時間 {self.default_minutes} 分鐘，計時開始！", 
                font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        # Store minutes in variable (not shown to user)
        self.minutes_var = tk.StringVar(value=str(self.default_minutes))
        
        # Single Start button
        tk.Button(main_frame, text="Start", command=self.on_start,
                 width=10, height=1, font=("Segoe UI", 11, "bold"), 
                 bg="green", fg="white").pack(pady=10)
        
        # Bind Enter key to start
        self.dialog.bind('<Return>', lambda e: self.on_start())
        self.dialog.bind('<Escape>', lambda e: self.on_escape())  # Esc shows reminder
        
        # Handle window close button - don't allow closing via X button
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close_attempt)
        
    def center_dialog(self):
        """Center the dialog over parent window"""
        self.dialog.update_idletasks()
        
        # Get dialog size
        dialog_width = 300
        dialog_height = 140
        
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
            
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
    def on_start(self):
        """Handle start button click"""
        try:
            minutes = int(self.minutes_var.get())
            if minutes <= 0:
                messagebox.showwarning("Invalid Input", "請輸入正數分鐘數", parent=self.dialog)
                return
            
            self.result = minutes
            self.dialog.destroy()
            INFO("Timer set for {} minutes", minutes)
            
        except ValueError:
            messagebox.showwarning("Invalid Input", "請輸入有效的數字", parent=self.dialog)
            
    def on_cancel(self):
        """Handle cancel button click - no longer used since we removed Cancel button"""
        self.result = None
        self.dialog.destroy()
        DEBUG("Timer setup cancelled")
    
    def on_escape(self):
        """Handle Escape key - show reminder instead of closing"""
        # Same as clicking X button
        self.on_close_attempt()
    
    def on_close_attempt(self):
        """Handle window close button (X) - prevent closing and show reminder"""
        # Flash the window to get attention
        self.dialog.bell()
        
        # Briefly change background color to indicate cannot close
        original_bg = self.dialog.cget('bg')
        self.dialog.configure(bg='#ffcccc')
        self.dialog.after(100, lambda: self.dialog.configure(bg=original_bg))
        
        # Show reminder message
        messagebox.showinfo(
            "開始遊戲", 
            "請按 Start 開始計時！",
            parent=self.dialog
        )
        
    def show(self):
        """Show dialog and wait for result"""
        self.dialog.wait_window()
        return self.result