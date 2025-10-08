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

        # Image context for coordinate conversion
        self._ctx = None

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
        
        
        # Edge detection threshold (optimized for small images)
        self.edge_threshold = 5
        self.corner_threshold = 8
        
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
        
        # Crosshair auxiliary lines state
        self.crosshair_vertical_id = None
        self.crosshair_horizontal_id = None
        self.crosshair_visible = False

    def set_image_context(self, ctx):
        """Set image context for coordinate conversion"""
        self._ctx = ctx
        DEBUG("BBoxController: Image context updated: {}", ctx if ctx else "None")

    def _is_within_image_area(self, x, y):
        """Check if coordinates are within actual image area (excluding black borders)"""
        if not self._ctx:
            return True  # If no context, assume all canvas is valid

        ox = self._ctx.get("ox", 0)
        oy = self._ctx.get("oy", 0)
        disp_w = self._ctx.get("disp_w", self.canvas.winfo_width())
        disp_h = self._ctx.get("disp_h", self.canvas.winfo_height())

        return ox <= x <= ox + disp_w and oy <= y <= oy + disp_h

    def _clamp_to_image_area(self, x, y):
        """Clamp coordinates to actual image area"""
        if not self._ctx:
            return x, y

        ox = self._ctx.get("ox", 0)
        oy = self._ctx.get("oy", 0)
        disp_w = self._ctx.get("disp_w", self.canvas.winfo_width())
        disp_h = self._ctx.get("disp_h", self.canvas.winfo_height())

        x = max(ox, min(x, ox + disp_w))
        y = max(oy, min(y, oy + disp_h))

        return x, y

    def toggle_drawing_mode(self):
        """Toggle drawing mode"""
        self.drawing_mode = not self.drawing_mode
        DEBUG("Drawing mode toggled to: {}", self.drawing_mode)

        # Update cursor style
        if self.drawing_mode:
            self.canvas.config(cursor="pencil")
        else:
            self.canvas.config(cursor="arrow")
            # Hide crosshair lines when exiting drawing mode
            self.hide_crosshair_lines()

        return self.drawing_mode

    def is_in_drawing_mode(self):
        """Check if in drawing mode"""
        return self.drawing_mode

    def start_drawing(self, x, y):
        """Start drawing bounding box"""
        if not self.drawing_mode:
            return False

        # Check if click is within actual image area
        if not self._is_within_image_area(x, y):
            DEBUG("Click outside image area at ({}, {}), ignoring", x, y)
            return False

        self.is_drawing = True
        self.draw_start_x = x
        self.draw_start_y = y
        DEBUG("Started drawing at ({}, {})", x, y)

        # Hide cursor to avoid obstructing view during drawing
        self.canvas.config(cursor="none")

        return True

    def update_preview(self, x, y):
        """Update preview box display"""
        if not self.is_drawing:
            return

        # Clamp coordinates to image area
        x, y = self._clamp_to_image_area(x, y)

        # Clear previous preview boxes
        if self.current_preview_id:
            self.canvas.delete(self.current_preview_id)
        self.canvas.delete("reference_box")  # Clear old reference box

        # Draw new preview box (cyan)
        self.current_preview_id = self.canvas.create_rectangle(
            self.draw_start_x, self.draw_start_y, x, y,
            outline="cyan", width=2, tags="preview_box"
        )
        
        # Check if we need to show gray reference box
        if hasattr(self, 'show_bbox_dimensions') and self.show_bbox_dimensions:
            if hasattr(self, 'min_width_threshold'):
                # Calculate current dragging width (canvas pixels)
                current_width = abs(x - self.draw_start_x)
                
                # Get canvas and original image dimensions
                original_width = getattr(self, 'original_image_width', 1920)
                displayed_width = getattr(self, 'displayed_image_width', self.canvas.winfo_width())
                
                # Calculate minimum width requirement (convert to canvas pixels)
                scale_x = displayed_width / float(original_width) if original_width else 1.0
                min_width_in_canvas = self.min_width_threshold * scale_x
                
                # Only show reference box when width is insufficient
                if current_width < min_width_in_canvas:
                    # Calculate reference box right boundary
                    if x > self.draw_start_x:
                        # Dragging to the right
                        ref_x2 = self.draw_start_x + min_width_in_canvas
                    else:
                        # Dragging to the left
                        ref_x2 = self.draw_start_x - min_width_in_canvas
                    
                    ref_y1 = min(self.draw_start_y, y)
                    ref_y2 = max(self.draw_start_y, y)
                    
                    # Draw yellow dashed reference box
                    self.canvas.create_rectangle(
                        min(self.draw_start_x, ref_x2), ref_y1, 
                        max(self.draw_start_x, ref_x2), ref_y2,
                        outline="yellow", width=1, dash=(10, 5), tags="reference_box"
                    )
        
        DEBUG("Updated preview box to ({}, {}, {}, {})", 
              self.draw_start_x, self.draw_start_y, x, y)

    def finish_drawing(self, x, y):
        """Complete drawing and return result"""
        if not self.is_drawing:
            return None

        # Clamp end point to image area
        x, y = self._clamp_to_image_area(x, y)

        self.is_drawing = False

        # Restore cursor to pencil when drawing finishes
        self.canvas.config(cursor="pencil")

        # Clear preview box and reference box
        if self.current_preview_id:
            self.canvas.delete(self.current_preview_id)
            self.current_preview_id = None
        self.canvas.delete("reference_box")  # Clear reference box too
        
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

        # Check if width meets threshold requirement (only for new bbox creation)
        if hasattr(self, 'show_bbox_dimensions') and self.show_bbox_dimensions:
            if hasattr(self, 'min_width_threshold'):
                # Get original image width and display width from context
                original_width = getattr(self, 'original_image_width', 1920)
                if self._ctx:
                    disp_w = self._ctx.get("disp_w", canvas_width)
                else:
                    disp_w = canvas_width

                # Calculate actual width in original pixels
                # width is in canvas pixels, convert to original image pixels
                actual_width_pixels = width * (original_width / disp_w)

                # Cancel if width is below threshold
                if actual_width_pixels < self.min_width_threshold:
                    DEBUG("Box width {} pixels below threshold {}, cancelled",
                          int(actual_width_pixels), self.min_width_threshold)
                    return None

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
        Convert canvas coordinates to YOLO format, accounting for black borders
        """
        # Get image context for proper coordinate conversion
        if self._ctx:
            ox = self._ctx.get("ox", 0)
            oy = self._ctx.get("oy", 0)
            disp_w = self._ctx.get("disp_w", canvas_w)
            disp_h = self._ctx.get("disp_h", canvas_h)

            # Convert canvas coordinates to image area coordinates
            # Subtract offset to get coordinates relative to actual image area
            img_x1 = x1 - ox
            img_y1 = y1 - oy
            img_x2 = x2 - ox
            img_y2 = y2 - oy

            # Calculate YOLO format based on actual image dimensions
            cx = (img_x1 + img_x2) / 2 / disp_w
            cy = (img_y1 + img_y2) / 2 / disp_h
            w_ratio = abs(img_x2 - img_x1) / disp_w
            h_ratio = abs(img_y2 - img_y1) / disp_h
        else:
            # Fallback to original calculation if no context
            cx = (x1 + x2) / 2 / canvas_w
            cy = (y1 + y2) / 2 / canvas_h
            w_ratio = abs(x2 - x1) / canvas_w
            h_ratio = abs(y2 - y1) / canvas_h

        return cx, cy, w_ratio, h_ratio

    def cancel_drawing(self):
        """Cancel current drawing"""
        if self.is_drawing:
            self.is_drawing = False

            # Restore cursor to pencil when drawing is cancelled
            self.canvas.config(cursor="pencil")

            if self.current_preview_id:
                self.canvas.delete(self.current_preview_id)
                self.current_preview_id = None
            self.canvas.delete("reference_box")  # Clear reference box too
            self.canvas.delete("resize_reference_box")  # Clear resize reference box too
            DEBUG("Drawing cancelled")

    def clear_preview(self):
        """Clear all preview boxes"""
        self.canvas.delete("preview_box")
        self.canvas.delete("reference_box")  # Clear reference box too
        self.canvas.delete("resize_reference_box")  # Clear resize reference box too
        self.current_preview_id = None

    def set_drawing_mode(self, mode):
        """Set drawing mode"""
        if self.drawing_mode != mode:
            self.toggle_drawing_mode()

    def create_label_object(self, yolo_coords, class_id=0):
        """Create LabelObject instance from YOLO coordinates"""
        cx, cy, w_ratio, h_ratio = yolo_coords
        return label_display_utils.LabelObject(class_id, cx, cy, w_ratio, h_ratio)

    def _is_near_edge(self, x, y, x1, y1, x2, y2, threshold=5):
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
            x, y (float): Point coordinates (canvas coordinates)
            label (LabelObject): Label object to check

        Returns:
            str: Edge type or None
        """
        # Get actual image dimensions and offset from context
        if self._ctx:
            disp_w = self._ctx.get("disp_w", self.canvas.winfo_width())
            disp_h = self._ctx.get("disp_h", self.canvas.winfo_height())
            ox = self._ctx.get("ox", 0)
            oy = self._ctx.get("oy", 0)
        else:
            disp_w = self.canvas.winfo_width()
            disp_h = self.canvas.winfo_height()
            ox = oy = 0

        # Convert label to canvas coordinates using actual image dimensions
        x1, y1, x2, y2 = label_display_utils.convert_label_to_canvas_coords(
            label, disp_w, disp_h)

        # Apply offset for black borders
        x1 += ox
        y1 += oy
        x2 += ox
        y2 += oy

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
        
        # In drawing mode: always show pencil cursor
        if self.drawing_mode:
            hover_info['cursor'] = 'pencil'
        else:
            # Normal mode: show appropriate cursor based on hover position
            # Focus mode: only check selected label
            if self.selected_label:
                edge_type = self.get_label_edge_type(x, y, self.selected_label)
                if edge_type:
                    hover_info['label'] = self.selected_label
                    hover_info['edge_type'] = edge_type
                    hover_info['cursor'] = self.get_cursor_for_edge_type(edge_type)
                else:
                    # Set default cursor when not over selected label
                    hover_info['cursor'] = 'arrow'
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
                    hover_info['cursor'] = 'arrow'
        
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
            x (float): 點擊的 x 座標 (canvas 像素)
            y (float): 點擊的 y 座標 (canvas 像素)
            labels (list): LabelObject 列表

        Returns:
            LabelObject or None: 選中的標籤對象，未選中時返回 None
        """
        # Prohibit selection in drawing mode
        if self.drawing_mode:
            DEBUG("Selection disabled in drawing mode")
            return None

        # Check from top layer (last drawn) first
        for label in reversed(labels):
            if self._label_contains_point(label, x, y):
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

    def _label_contains_point(self, label, x, y):
        """
        Check if a point is inside a label's bounding box

        Args:
            label (LabelObject): Label to check
            x, y (float): Point coordinates (canvas coordinates)

        Returns:
            bool: True if point is inside label
        """
        # Get actual image dimensions and offset from context
        if self._ctx:
            disp_w = self._ctx.get("disp_w", self.canvas.winfo_width())
            disp_h = self._ctx.get("disp_h", self.canvas.winfo_height())
            ox = self._ctx.get("ox", 0)
            oy = self._ctx.get("oy", 0)
        else:
            disp_w = self.canvas.winfo_width()
            disp_h = self.canvas.winfo_height()
            ox = oy = 0

        # Convert label to canvas coordinates using actual image dimensions
        x1, y1, x2, y2 = label_display_utils.convert_label_to_canvas_coords(
            label, disp_w, disp_h)

        # Apply offset for black borders
        x1 += ox
        y1 += oy
        x2 += ox
        y2 += oy

        # Check if point is inside rectangle
        return x1 <= x <= x2 and y1 <= y <= y2

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
        # Prohibit dragging in drawing mode
        if self.drawing_mode:
            DEBUG("Dragging disabled in drawing mode")
            return False

        # 檢查是否有選中的標籤且點擊在其內部
        if self.selected_label and self._label_contains_point(self.selected_label, x, y):
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

        # Clamp coordinates to image area
        x, y = self._clamp_to_image_area(x, y)

        # 計算位移量
        dx = x - self.drag_start_x
        dy = y - self.drag_start_y

        if dx == 0 and dy == 0:
            return

        # Get actual image dimensions from context
        if self._ctx:
            disp_w = self._ctx.get("disp_w", self.canvas.winfo_width())
            disp_h = self._ctx.get("disp_h", self.canvas.winfo_height())
        else:
            disp_w = self.canvas.winfo_width()
            disp_h = self.canvas.winfo_height()

        # 移動標籤 (使用實際圖片尺寸而非canvas尺寸)
        self.dragging_label.move_by_canvas_delta(dx, dy, disp_w, disp_h)
        
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

        # Clamp coordinates to image area
        x, y = self._clamp_to_image_area(x, y)

        # Clear old reference box
        self.canvas.delete("resize_reference_box")

        # 計算位移量
        dx = x - self.resize_start_x
        dy = y - self.resize_start_y

        # 更新起始位置
        self.resize_start_x, self.resize_start_y = x, y

        # Get actual image dimensions from context
        if self._ctx:
            disp_w = self._ctx.get("disp_w", self.canvas.winfo_width())
            disp_h = self._ctx.get("disp_h", self.canvas.winfo_height())
            ox = self._ctx.get("ox", 0)
            oy = self._ctx.get("oy", 0)
        else:
            disp_w = self.canvas.winfo_width()
            disp_h = self.canvas.winfo_height()
            ox = oy = 0

        # 使用 resize_by_delta 方法調整大小，使用實際圖片尺寸
        self.resizing_label.resize_by_delta(dx, dy, disp_w, disp_h, self.resize_handle_type)
        
        # Check if we need to show reference box during resize
        if hasattr(self, 'show_bbox_dimensions') and self.show_bbox_dimensions:
            if hasattr(self, 'min_width_threshold') and self.resizing_label:
                # Get original image width
                original_width = getattr(self, 'original_image_width', 1920)
                
                # Calculate current box width in original pixels
                actual_bbox_width = int(self.resizing_label.w_ratio * original_width)
                
                # Only show reference box when width is insufficient
                if actual_bbox_width < self.min_width_threshold:
                    # Calculate box position on canvas (with offset)
                    x1 = (self.resizing_label.cx_ratio - self.resizing_label.w_ratio/2) * disp_w + ox
                    y1 = (self.resizing_label.cy_ratio - self.resizing_label.h_ratio/2) * disp_h + oy
                    y2 = (self.resizing_label.cy_ratio + self.resizing_label.h_ratio/2) * disp_h + oy

                    # Calculate reference width in canvas pixels
                    ref_width_canvas = self.min_width_threshold * (disp_w / original_width)
                    ref_x2 = x1 + ref_width_canvas

                    # Draw yellow dashed reference box
                    self.canvas.create_rectangle(
                        x1, y1, ref_x2, y2,
                        outline="yellow", width=1, dash=(10, 5), tags="resize_reference_box"
                    )
        
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
        
        # Clear reference box
        self.canvas.delete("resize_reference_box")
        
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
        # Prohibit all operations in drawing mode
        if self.drawing_mode:
            DEBUG("Mouse press operations disabled in drawing mode")
            return "none"
            
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
    
    def show_crosshair_lines(self, x, y):
        """
        Display crosshair auxiliary lines at the specified position
        
        Args:
            x, y (int): Position coordinates on canvas
        """
        if not self.drawing_mode:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Hide existing lines first
        self.hide_crosshair_lines()
        
        # Create vertical line (x=constant, y from 0 to canvas_height)
        self.crosshair_vertical_id = self.canvas.create_line(
            x, 0, x, canvas_height,
            fill="#00BFFF", width=2, dash=(2, 2), tags="crosshair_lines"
        )
        
        # Create horizontal line (y=constant, x from 0 to canvas_width)  
        self.crosshair_horizontal_id = self.canvas.create_line(
            0, y, canvas_width, y,
            fill="#00BFFF", width=2, dash=(2, 2), tags="crosshair_lines"
        )
        
        self.crosshair_visible = True
        
    def hide_crosshair_lines(self):
        """Hide crosshair auxiliary lines"""
        if self.crosshair_vertical_id:
            self.canvas.delete(self.crosshair_vertical_id)
            self.crosshair_vertical_id = None
            
        if self.crosshair_horizontal_id:
            self.canvas.delete(self.crosshair_horizontal_id)
            self.crosshair_horizontal_id = None
            
        # Also delete by tags as a safety measure
        self.canvas.delete("crosshair_lines")
        self.crosshair_visible = False
        
    def update_crosshair_position(self, x, y):
        """
        Update crosshair lines position
        
        Args:
            x, y (int): New position coordinates on canvas
        """
        if self.drawing_mode:
            # Simply recreate the lines at new position
            self.show_crosshair_lines(x, y)
        else:
            # Hide lines if not in drawing mode
            self.hide_crosshair_lines()

class DrawingState:
    """Drawing state enumeration"""
    IDLE = "idle"
    DRAWING = "drawing"
    PREVIEW = "preview"
    RESIZING = "resizing"  # 添加 resizing 狀態