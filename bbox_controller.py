"""
BBox Controller Module
Manages bounding box drawing, selection, dragging, and resizing operations
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
        
        # Dragging state variables
        self.dragging_label = None      # Currently dragging LabelObject
        self.drag_start_x = 0           # Drag start X coordinate (canvas)
        self.drag_start_y = 0           # Drag start Y coordinate (canvas)
        self.is_dragging = False        # Dragging in progress flag
        
        # Resizing state variables
        self.resizing_label = None      # Currently resizing LabelObject  
        self.resize_start_x = 0         # Resize start X coordinate (canvas)
        self.resize_start_y = 0         # Resize start Y coordinate (canvas)
        self.is_resizing = False        # Resizing in progress flag
        self.resize_handle_type = None  # Track which handle is being dragged
        
        # Minimum box size constraints
        self.min_box_width = 5
        self.min_box_height = 5
        
        
        # Edge detection threshold
        self.edge_threshold = 8
        self.corner_threshold = 15
        
        # Cursor mapping for different edge types
        self.cursor_map = {
            'top': 'sb_v_double_arrow',
            'bottom': 'sb_v_double_arrow', 
            'left': 'sb_h_double_arrow',
            'right': 'sb_h_double_arrow',
            'tl': 'top_left_corner',     # top-left corner: ↖
            'tr': 'top_right_corner',    # top-right corner: ↗
            'bl': 'bottom_left_corner',  # bottom-left corner: ↙  
            'br': 'bottom_right_corner', # bottom-right corner: ↘
            'inside': 'fleur'            # move cursor: ✚
        }
        
        # Current hover state
        self.current_hover_label = None
        self.current_edge_type = None

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
        Convert YOLO coordinates to canvas pixel coordinates
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

    def _is_near_edge(self, x, y, x1, y1, x2, y2, threshold=8):
        """
        Check if point (x, y) is near any edge or inside the bounding box
        
        Args:
            x, y (float): Point coordinates
            x1, y1, x2, y2 (float): Bounding box coordinates
            threshold (int): Distance threshold for edge detection
            
        Returns:
            bool: True if point is near any edge or inside the box
        """
        # Check if point is within the expanded box (edge detection area)
        expanded_x1 = x1 - threshold
        expanded_y1 = y1 - threshold
        expanded_x2 = x2 + threshold
        expanded_y2 = y2 + threshold
        
        # Point must be within expanded area OR inside the original box
        inside_original = x1 <= x <= x2 and y1 <= y <= y2
        inside_expanded = expanded_x1 <= x <= expanded_x2 and expanded_y1 <= y <= expanded_y2
        
        if not (inside_expanded or inside_original):
            return False
        
        # If inside original box, always return True (covers both edges and center)
        if inside_original:
            return True
        
        # If in expanded area but outside original box, check if near edges
        near_left = abs(x - x1) <= threshold
        near_right = abs(x - x2) <= threshold
        near_top = abs(y - y1) <= threshold
        near_bottom = abs(y - y2) <= threshold
        
        inside_x = x1 <= x <= x2
        inside_y = y1 <= y <= y2
        
        # Near edge conditions for expanded area
        near_vertical_edge = (near_left or near_right) and inside_y
        near_horizontal_edge = (near_top or near_bottom) and inside_x
        near_corner = (near_left or near_right) and (near_top or near_bottom)
        
        return near_vertical_edge or near_horizontal_edge or near_corner

    def _get_edge_type(self, x, y, x1, y1, x2, y2):
        """
        Determine which edge/corner the point is near
        
        Args:
            x, y (float): Point coordinates  
            x1, y1, x2, y2 (float): Bounding box coordinates
            
        Returns:
            str: Edge type ('top', 'bottom', 'left', 'right', 'tl', 'tr', 'bl', 'br', 'inside', None)
        """
        corner_threshold = self.corner_threshold
        edge_threshold = self.edge_threshold
        
        # Check if point is within detection area
        if not self._is_near_edge(x, y, x1, y1, x2, y2, edge_threshold):
            return None
        
        # Check corners first (higher priority)
        near_left = abs(x - x1) <= corner_threshold
        near_right = abs(x - x2) <= corner_threshold  
        near_top = abs(y - y1) <= corner_threshold
        near_bottom = abs(y - y2) <= corner_threshold
        
        # Corner detection
        if near_left and near_top:
            return 'tl'  # top-left
        elif near_right and near_top:
            return 'tr'  # top-right
        elif near_left and near_bottom:
            return 'bl'  # bottom-left
        elif near_right and near_bottom:
            return 'br'  # bottom-right
        
        # Edge detection (lower priority than corners)
        near_left_edge = abs(x - x1) <= edge_threshold
        near_right_edge = abs(x - x2) <= edge_threshold
        near_top_edge = abs(y - y1) <= edge_threshold
        near_bottom_edge = abs(y - y2) <= edge_threshold
        
        inside_x = x1 <= x <= x2
        inside_y = y1 <= y <= y2
        
        if near_left_edge and inside_y:
            return 'left'
        elif near_right_edge and inside_y:
            return 'right'
        elif near_top_edge and inside_x:
            return 'top'
        elif near_bottom_edge and inside_x:
            return 'bottom'
        
        # Check if inside the box
        if inside_x and inside_y:
            return 'inside'
        
        return None

    def get_label_edge_type(self, x, y, label):
        """
        Get edge type for a specific label
        
        Args:
            x, y (float): Point coordinates
            label (LabelObject): Label object to check
            
        Returns:
            str: Edge type or None
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Convert label to canvas coordinates
        x1, y1, x2, y2 = label_display_utils.convert_label_to_canvas_coords(
            label, canvas_width, canvas_height)
        
        return self._get_edge_type(x, y, x1, y1, x2, y2)

    def get_cursor_for_edge_type(self, edge_type):
        """
        Get appropriate cursor for edge type
        
        Args:
            edge_type (str): Edge type ('top', 'left', 'tl', etc.)
            
        Returns:
            str: Cursor name
        """
        return self.cursor_map.get(edge_type, 'arrow')

    def update_cursor_for_position(self, x, y, labels):
        """
        Update cursor based on mouse position and labels
        Implements dual-mode logic: focus mode vs quick mode
        
        Args:
            x, y (float): Mouse position
            labels (list): List of LabelObject instances
            
        Returns:
            dict: Information about hover state
        """
        hover_info = {
            'label': None,
            'edge_type': None,
            'cursor': 'arrow'
        }
        
        # Focus mode: only check selected label
        if self.selected_label:
            edge_type = self.get_label_edge_type(x, y, self.selected_label)
            if edge_type:
                hover_info['label'] = self.selected_label
                hover_info['edge_type'] = edge_type
                hover_info['cursor'] = self.get_cursor_for_edge_type(edge_type)
            else:
                # Set default cursor when not over selected label
                hover_info['cursor'] = 'pencil' if self.drawing_mode else 'arrow'
        else:
            # Quick mode: check all labels (top layer first)
            for label in reversed(labels):
                edge_type = self.get_label_edge_type(x, y, label)
                if edge_type:
                    hover_info['label'] = label
                    hover_info['edge_type'] = edge_type
                    hover_info['cursor'] = self.get_cursor_for_edge_type(edge_type)
                    break
            else:
                # No label under cursor
                hover_info['cursor'] = 'pencil' if self.drawing_mode else 'arrow'
        
        # Update cursor if it changed
        if hover_info['cursor'] != self.canvas.cget('cursor'):
            self.canvas.config(cursor=hover_info['cursor'])
        
        # Update hover state
        self.current_hover_label = hover_info['label']
        self.current_edge_type = hover_info['edge_type']
        
        return hover_info

    def handle_selection(self, x, y, labels):
        """
        處理點擊選擇邏輯，最上層標籤優先
        
        Args:
            x (float): 點擊的 x 座標
            y (float): 點擊的 y 座標
            labels (list): LabelObject 列表
            
        Returns:
            LabelObject or None: 選中的標籤對象，未選中時返回 None
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Check from top layer (last drawn) first
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
        
        # Clear selection if no label was clicked
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
        初始化拖曳操作
        
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
        處理拖曳移動
        
        Args:
            x (float): 當前 X 座標 (canvas 像素)
            y (float): 當前 Y 座標 (canvas 像素)
        """
        if not self.is_dragging or not self.dragging_label:
            return
            
        # 計算位移量
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
        完成拖曳操作
        
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



    def update_resize(self, x, y):
        """
        處理 resize 移動
        
        Args:
            x (float): 當前 X 座標 (canvas 像素)
            y (float): 當前 Y 座標 (canvas 像素)
        """
        if not self.is_resizing or not self.resizing_label:
            return
            
        # 計算位移量
        dx = x - self.resize_start_x
        dy = y - self.resize_start_y
        
        # 更新起始位置
        self.resize_start_x, self.resize_start_y = x, y
        
        # 獲取 canvas 尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 使用 resize_by_delta 方法調整大小，傳入 handle 類型
        self.resizing_label.resize_by_delta(dx, dy, canvas_width, canvas_height, self.resize_handle_type)
        
        DEBUG("Resizing label moved by delta ({}, {}), new size=({:.3f}, {:.3f})", 
              dx, dy, self.resizing_label.w_ratio, self.resizing_label.h_ratio)

    def finish_resize(self):
        """
        完成 resize 操作
        
        Returns:
            LabelObject or None: 被 resize 的標籤對象，如果有的話
        """
        if not self.is_resizing:
            return None
            
        resized_label = self.resizing_label
        
        # 清除 resizing 狀態
        self.is_resizing = False
        self.resizing_label = None
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_handle_type = None
        
        # 恢復光標樣式
        if self.drawing_mode:
            self.canvas.config(cursor="pencil")
        else:
            self.canvas.config(cursor="arrow")
            
        if resized_label:
            DEBUG("Finished resizing label: class_id={}, final size=({:.3f}, {:.3f})", 
                  resized_label.class_id, resized_label.w_ratio, resized_label.h_ratio)
            
        return resized_label

    def start_edge_resize(self, x, y, label, edge_type):
        """
        開始基於邊緣的 resize 操作
        
        Args:
            x (float): 點擊起始 X 座標 (canvas 像素)
            y (float): 點擊起始 Y 座標 (canvas 像素)
            label (LabelObject): 要 resize 的標籤
            edge_type (str): 邊緣類型
            
        Returns:
            bool: 是否成功開始 resize
        """
        if not label or not edge_type or edge_type == 'inside':
            return False
        
        self.is_resizing = True
        self.resizing_label = label
        self.resize_start_x = x
        self.resize_start_y = y
        
        # Convert edge type to handle type for compatibility
        edge_to_handle_map = {
            'top': 'top',
            'bottom': 'bottom', 
            'left': 'left',
            'right': 'right',
            'tl': 'top-left',
            'tr': 'top-right',
            'bl': 'bottom-left',
            'br': 'bottom-right'
        }
        self.resize_handle_type = edge_to_handle_map.get(edge_type, 'bottom-right')
        
        # Set cursor
        cursor = self.get_cursor_for_edge_type(edge_type)
        self.canvas.config(cursor=cursor)
        
        DEBUG("Started edge resize: label class_id={}, edge_type={}, start_pos=({}, {})", 
              label.class_id, edge_type, x, y)
        return True

    def handle_mouse_press_with_resize(self, x, y, labels):
        """
        處理滑鼠按下事件，支援邊緣 resize
        
        Args:
            x (float): 點擊的 X 座標 (canvas 像素)
            y (float): 點擊的 Y 座標 (canvas 像素)
            labels (list): LabelObject 列表
            
        Returns:
            str: 操作類型 ("resize", "drag", "select", "none")
        """
        # Focus mode: if we have a selected label
        if self.selected_label:
            edge_type = self.get_label_edge_type(x, y, self.selected_label)
            if edge_type:
                if edge_type == 'inside':
                    # Start dragging the selected label
                    if self.start_drag(x, y, labels):
                        return "drag"
                else:
                    # Start resizing the selected label
                    if self.start_edge_resize(x, y, self.selected_label, edge_type):
                        return "resize"
            else:
                # Clicked outside selected label - check for selection change
                selected_label = self.handle_selection(x, y, labels)
                if selected_label:
                    return "select"
                else:
                    return "none"
        else:
            # Quick mode: no selected label
            # Check all labels for direct interaction
            for label in reversed(labels):  # Top layer first
                edge_type = self.get_label_edge_type(x, y, label)
                if edge_type:
                    if edge_type == 'inside':
                        # Direct drag - start dragging and auto-select
                        self.handle_selection(x, y, labels)  # Select the label
                        if self.start_drag(x, y, labels):
                            return "drag"
                    else:
                        # Direct resize - start resizing and auto-select  
                        self.handle_selection(x, y, labels)  # Select the label
                        if self.start_edge_resize(x, y, label, edge_type):
                            return "resize"
                    break
            else:
                # No label under cursor - just handle selection
                selected_label = self.handle_selection(x, y, labels)
                if selected_label:
                    return "select"
        
        return "none"

class DrawingState:
    """Drawing state enumeration"""
    IDLE = "idle"
    DRAWING = "drawing"
    PREVIEW = "preview"
    RESIZING = "resizing"  # 添加 resizing 狀態