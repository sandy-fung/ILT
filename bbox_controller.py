"""
BBox Controller Module
Reuse drawing logic from image_label_tool for managing bounding box drawing and operations
"""

import tkinter as tk
from log_levels import DEBUG, INFO, ERROR
import label_display_utils

class BBoxController:
    def __init__(self, canvas):
        self.canvas = canvas
        self.drawing_mode = False
        self.is_drawing = False
        
        # Drawing state variables
        self.draw_start_x = 0
        self.draw_start_y = 0
        self.current_preview_id = None
        
        # Minimum box size constraints
        self.min_box_width = 5
        self.min_box_height = 5

    def toggle_drawing_mode(self):
        """Toggle drawing mode"""
        self.drawing_mode = not self.drawing_mode
        DEBUG("Drawing mode toggled to: {}", self.drawing_mode)
        
        # Update cursor style
        if self.drawing_mode:
            self.canvas.config(cursor="pencil")
        else:
            self.canvas.config(cursor="arrow")
            
        return self.drawing_mode

    def is_in_drawing_mode(self):
        """Check if in drawing mode"""
        return self.drawing_mode

    def start_drawing(self, x, y):
        """Start drawing bounding box"""
        if not self.drawing_mode:
            return False
            
        self.is_drawing = True
        self.draw_start_x = x
        self.draw_start_y = y
        DEBUG("Started drawing at ({}, {})", x, y)
        return True

    def update_preview(self, x, y):
        """Update preview box display"""
        if not self.is_drawing:
            return
            
        # Clear previous preview box
        if self.current_preview_id:
            self.canvas.delete(self.current_preview_id)
        
        # Draw new preview box
        self.current_preview_id = self.canvas.create_rectangle(
            self.draw_start_x, self.draw_start_y, x, y,
            outline="cyan", width=2, tags="preview_box"
        )
        DEBUG("Updated preview box to ({}, {}, {}, {})", 
              self.draw_start_x, self.draw_start_y, x, y)

    def finish_drawing(self, x, y):
        """Complete drawing and return result"""
        if not self.is_drawing:
            return None
            
        self.is_drawing = False
        
        # Clear preview box
        if self.current_preview_id:
            self.canvas.delete(self.current_preview_id)
            self.current_preview_id = None
        
        # Calculate actual box coordinates (ensure top-left to bottom-right)
        x1 = min(self.draw_start_x, x)
        y1 = min(self.draw_start_y, y)
        x2 = max(self.draw_start_x, x)
        y2 = max(self.draw_start_y, y)
        
        # Check minimum size
        width = x2 - x1
        height = y2 - y1
        
        if width < self.min_box_width or height < self.min_box_height:
            DEBUG("Box too small: {}x{}, ignored", width, height)
            return None
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculate YOLO format coordinates
        yolo_coords = self.calculate_yolo_format(x1, y1, x2, y2, canvas_width, canvas_height)
        
        result = {
            'canvas_coords': (x1, y1, x2, y2),
            'yolo_coords': yolo_coords,
            'size': (width, height)
        }
        
        DEBUG("Finished drawing: canvas=({}, {}, {}, {}), yolo=({:.6f}, {:.6f}, {:.6f}, {:.6f})", 
              x1, y1, x2, y2, *yolo_coords)
        
        return result

    def calculate_yolo_format(self, x1, y1, x2, y2, canvas_w, canvas_h):
        """
        Calculate YOLO format coordinates (center_x, center_y, width_ratio, height_ratio)
        Reuse conversion logic from image_label_tool
        """
        cx = (x1 + x2) / 2 / canvas_w
        cy = (y1 + y2) / 2 / canvas_h
        w_ratio = abs(x2 - x1) / canvas_w
        h_ratio = abs(y2 - y1) / canvas_h
        return cx, cy, w_ratio, h_ratio

    def cancel_drawing(self):
        """Cancel current drawing"""
        if self.is_drawing:
            self.is_drawing = False
            if self.current_preview_id:
                self.canvas.delete(self.current_preview_id)
                self.current_preview_id = None
            DEBUG("Drawing cancelled")

    def clear_preview(self):
        """Clear all preview boxes"""
        self.canvas.delete("preview_box")
        self.current_preview_id = None

    def set_drawing_mode(self, mode):
        """Set drawing mode"""
        if self.drawing_mode != mode:
            self.toggle_drawing_mode()

    def create_label_object(self, yolo_coords, class_id=0):
        """Create LabelObject instance from YOLO coordinates"""
        cx, cy, w_ratio, h_ratio = yolo_coords
        return label_display_utils.LabelObject(class_id, cx, cy, w_ratio, h_ratio)

class DrawingState:
    """Drawing state enumeration"""
    IDLE = "idle"
    DRAWING = "drawing"
    PREVIEW = "preview"