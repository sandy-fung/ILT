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
        
        # Selection state variables
        self.selected_label = None
        
        # Dragging state variables (reuse pattern from image_label_tool)
        self.dragging_label = None      # Currently dragging LabelObject
        self.drag_start_x = 0           # Drag start X coordinate (canvas)
        self.drag_start_y = 0           # Drag start Y coordinate (canvas)
        self.is_dragging = False        # Dragging in progress flag
        
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

    def handle_selection(self, x, y, labels):
        """
        處理點擊選擇邏輯，按照 z-index 順序 (最上層優先)
        
        Args:
            x (float): 點擊的 x 座標
            y (float): 點擊的 y 座標
            labels (list): LabelObject 列表
            
        Returns:
            LabelObject or None: 選中的標籤對象，如果沒有選中則返回 None
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 從最後一個開始檢查 (最上層的 bounding box)
        for label in reversed(labels):
            if label.contains(x, y, canvas_width, canvas_height):
                # 清除所有標籤的選中狀態
                self.clear_selection(labels)
                
                # 設定當前標籤為選中
                label.set_selected(True)
                self.selected_label = label
                
                DEBUG("Selected label: class_id={}, coords=({:.3f}, {:.3f}, {:.3f}, {:.3f})", 
                      label.class_id, label.cx_ratio, label.cy_ratio, label.w_ratio, label.h_ratio)
                return label
        
        # 如果沒有點擊在任何標籤上，清除選擇
        self.clear_selection(labels)
        return None

    def clear_selection(self, labels):
        """
        清除所有標籤的選中狀態
        
        Args:
            labels (list): LabelObject 列表
        """
        for label in labels:
            label.set_selected(False)
        
        self.selected_label = None
        DEBUG("Cleared all selections")

    def get_selected_label(self):
        """
        獲取當前選中的標籤
        
        Returns:
            LabelObject or None: 當前選中的標籤
        """
        return self.selected_label

    def start_drag(self, x, y, labels):
        """
        初始化拖曳操作 (複用 image_label_tool 的模式)
        
        Args:
            x (float): 拖曳起始 X 座標 (canvas 像素)
            y (float): 拖曳起始 Y 座標 (canvas 像素)  
            labels (list): LabelObject 列表
            
        Returns:
            bool: 是否成功開始拖曳
        """
        # 檢查是否有選中的標籤且點擊在其內部
        if self.selected_label and self.selected_label.contains(x, y, 
                                                               self.canvas.winfo_width(), 
                                                               self.canvas.winfo_height()):
            self.is_dragging = True
            self.dragging_label = self.selected_label
            self.drag_start_x = x
            self.drag_start_y = y
            
            # 更改光標樣式
            self.canvas.config(cursor="fleur")
            
            DEBUG("Started dragging label: class_id={}, coords=({:.3f}, {:.3f}, {:.3f}, {:.3f})", 
                  self.dragging_label.class_id, self.dragging_label.cx_ratio, 
                  self.dragging_label.cy_ratio, self.dragging_label.w_ratio, self.dragging_label.h_ratio)
            return True
        
        return False

    def update_drag(self, x, y):
        """
        處理拖曳移動 (複用 image_label_tool 的增量計算模式)
        
        Args:
            x (float): 當前 X 座標 (canvas 像素)
            y (float): 當前 Y 座標 (canvas 像素)
        """
        if not self.is_dragging or not self.dragging_label:
            return
            
        # 計算位移量 (複用參考實現的 delta 方式)
        dx = x - self.drag_start_x
        dy = y - self.drag_start_y
        
        if dx == 0 and dy == 0:
            return
            
        # 獲取 canvas 尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 移動標籤 (使用 canvas 像素增量)
        self.dragging_label.move_by_canvas_delta(dx, dy, canvas_width, canvas_height)
        
        # 更新拖曳起始位置
        self.drag_start_x = x
        self.drag_start_y = y
        
        DEBUG("Dragging label moved by delta ({}, {}), new coords=({:.3f}, {:.3f})", 
              dx, dy, self.dragging_label.cx_ratio, self.dragging_label.cy_ratio)

    def finish_drag(self):
        """
        完成拖曳操作 (複用 image_label_tool 的清理模式)
        
        Returns:
            LabelObject or None: 被拖曳的標籤對象，如果有的話
        """
        if not self.is_dragging:
            return None
            
        dragged_label = self.dragging_label
        
        # 清除拖曳狀態
        self.is_dragging = False
        self.dragging_label = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # 恢復光標樣式
        if self.drawing_mode:
            self.canvas.config(cursor="pencil")
        else:
            self.canvas.config(cursor="arrow")
            
        if dragged_label:
            DEBUG("Finished dragging label: class_id={}, final coords=({:.3f}, {:.3f}, {:.3f}, {:.3f})", 
                  dragged_label.class_id, dragged_label.cx_ratio, 
                  dragged_label.cy_ratio, dragged_label.w_ratio, dragged_label.h_ratio)
            
        return dragged_label

class DrawingState:
    """Drawing state enumeration"""
    IDLE = "idle"
    DRAWING = "drawing"
    PREVIEW = "preview"