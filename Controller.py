from UI_event import UIEvent
import config_utils
import image_utils
import folder_utils
import label_display_utils
import Words_Label_mapping as wlm
import char_input_handler as char_handler
import os
from log_levels import DEBUG, INFO, ERROR

class Controller:
    def __init__(self, view):
        self.view = view

        self.image_folder_path = None
        self.label_folder_path = None
        self.images = []
        self.labels = []
        self.images_path = []
        self.labels_path = []
        self.current_labels = []  # List of LabelObject instances for current image
        self.image_index = 0
        self.image_width = 0
        self.image_height = 0
        
        # Drawing mode state
        self.drawing_mode = False
        
        # Dragging redraw strategy (複用 image_label_tool 的完整重繪策略)
        self.check_config()



    def check_config(self):
        self.image_folder_path = config_utils.get_image_folder_path()
        self.label_folder_path = config_utils.get_label_folder_path()
        if not self.image_folder_path or not self.label_folder_path:
            self.select_folders()
        else:
            self.load_folder()

    def select_folders(self):
        self.image_folder_path = self.view.select_folder("Select Image Folder")
        if not self.image_folder_path:
            msg = "No image folder selected."
            ERROR(msg)
            raise  Exception(msg)
        self.label_folder_path = self.view.select_folder("Select Label Folder")
        if not self.label_folder_path:
            msg = "No label folder selected."
            ERROR(msg)
            raise  Exception(msg)

        self.load_folder()
        DEBUG("save_path:{}, {}", self.image_folder_path, self.label_folder_path)

        # Save paths to config
        config_utils.save_paths(self.image_folder_path, self.label_folder_path)

        # Reset image index
        self.image_index = 0
        config_utils.save_image_index(self.image_index)

        self.load_image(self.images_path)

    def load_folder(self):
        # load image folder
        self.images, self.images_path = folder_utils.scan_image_folder(self.image_folder_path)

        # load label folder
        self.labels, self.labels_path = folder_utils.scan_label_folder(self.images, self.label_folder_path)
        folder_utils.ensure_labels_exist(self.labels_path)
        
        # Load the current image and labels
        self.image_index = config_utils.get_image_index()
        if self.images_path:
            self.load_image(self.images_path)

    def load_image(self, imgs_path):
        index = config_utils.get_image_index()
        image_path = imgs_path[index]

        self.original_image = image_utils.load_image(image_path)

        self.update_resized_image()

    def update_resized_image(self):
        if self.original_image is None:
            ERROR("No original image to resize.")
            return
        DEBUG("Controller.update_resized_image() called")

        canvas_height, canvas_width = self.view.get_canvas_size()
        if canvas_height == 0 or canvas_width == 0:
            ERROR("Failed to get canvas size.")
            return

        resized = image_utils.resize_image(self.original_image, (canvas_width, canvas_height))
        self.image = image_utils.convert_to_tk(resized)

        self.view.update_image_canvas(self.image)
        DEBUG("Controller.load_image() completed")
        self.view.update_index_label(self.image_index, self.images_path)
        
        # Parse and draw labels for current image
        self.parse_current_labels()
        if self.current_labels:
            DEBUG("Drawing {} labels on canvas", len(self.current_labels))
            self.view.draw_labels_on_canvas(self.current_labels)

    def load_label(self, path):
        try:
            content = folder_utils.load_label(self.labels_path[self.image_index])
        except FileNotFoundError:
            ERROR("Label file not found at path:", path[self.image_index])
            content = "(Label file not found)"
        except Exception as e:
            ERROR("Error loading label file:", e)
            content = "(Error loading label file)"

        self.view.update_text_box(content)
        
        # Labels are already parsed and drawn in update_resized_image()

    def parse_current_labels(self):
        """Parse current image's label file and store LabelObject instances"""
        if self.image_index < len(self.labels_path):
            current_label_path = self.labels_path[self.image_index]
            self.current_labels = label_display_utils.parse_label_file(current_label_path)
            DEBUG("Parsed {} labels for current image", len(self.current_labels))
            
            # 自動排序標籤
            if self.current_labels:
                original_count = len(self.current_labels)
                self.current_labels, plate_count = label_display_utils.sort_labels_by_position(self.current_labels)
                DEBUG("Auto-sorted {} labels by position in {} plates", original_count, plate_count)
                # 保存排序後的標籤
                self.save_current_labels()
                # 更新文字框顯示排序後的標籤
                self.load_label(self.labels_path)
                # 更新狀態顯示
                if hasattr(self.view, 'update_sorting_status'):
                    self.view.update_sorting_status(original_count, plate_count)
        else:
            self.current_labels = []
            ERROR("Invalid image index for label parsing: {}", self.image_index)

    def next_image(self):
        DEBUG("Current image index:", self.image_index)
        if self.image_index < len(self.images) - 1:
            self.image_index += 1
        config_utils.save_image_index(self.image_index)

        self.load_image(self.images_path)
        self.load_label(self.labels_path)

    def previous_image(self):
        DEBUG("Current image index:", self.image_index)
        if self.image_index > 0:
            self.image_index -= 1
        config_utils.save_image_index(self.image_index)
        
        self.load_image(self.images_path)
        self.load_label(self.labels_path)

    def handle_event(self, event_type, event_data):
        if event_type == UIEvent.WINDOW_READY:
            INFO("Controller: Window is ready.")
            self.load_image(self.images_path)
            self.load_label(self.labels_path)
            self.view.show_class_id_buttons(config_utils.get_class_id_vars(), wlm.get_labels())

        elif event_type == UIEvent.CANVAS_RESIZE:
            DEBUG("Controller: Canvas resized.")
            self.update_resized_image()

        elif event_type == UIEvent.LEFT_CTRL_PRESS:
            DEBUG("Controller: Left Ctrl pressed.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do L-CTRL EVENT")
            
        elif event_type == UIEvent.DRAWING_MODE_TOGGLE:
            DEBUG("Controller: Drawing mode toggle.")
            self.drawing_mode = event_data.get("drawing_mode", False)
            DEBUG("Drawing mode set to: {}", self.drawing_mode)  

        elif event_type == UIEvent.RIGHT_CTRL_PRESS:
            DEBUG("Controller: Right Ctrl pressed.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do R-CTRL EVENT")

        elif event_type == UIEvent.RIGHT_CTRL_RELEASE:
            DEBUG("Controller: Right Ctrl released.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do R-CTRL RELEASE EVENT")

        elif event_type == UIEvent.RIGHT_PRESS:
            DEBUG("Controller: Right pressed.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do R-Press EVENT")
            self.next_image()

        elif event_type == UIEvent.LEFT_PRESS:
            DEBUG("Controller: Left pressed.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do L-Press EVENT")
            self.previous_image()

        elif event_type == UIEvent.MOUSE_LEFT_CLICK:
            DEBUG("Controller: Mouse Left clicked.")
            DEBUG("entry_value", event_data.get("value"))
            DEBUG("do MOUSE-L EVENT")

        elif event_type == UIEvent.MOUSE_RIGHT_CLICK:
            DEBUG("Controller: Mouse Right clicked.")
            event = event_data.get("value")
            DEBUG("Right click at ({}, {})", event.x, event.y)
            
            # 取得 bbox_controller 從 view
            bbox_controller = getattr(self.view, 'bbox_controller', None)
            if bbox_controller and bbox_controller.get_selected_label():
                # 如果有選中的標籤，檢查右鍵是否點擊在選中的標籤上
                selected_label = bbox_controller.get_selected_label()
                canvas_width = self.view.get_canvas_size()[1]
                canvas_height = self.view.get_canvas_size()[0]
                if selected_label.contains(event.x, event.y, canvas_width, canvas_height):
                    # 顯示右鍵菜單 (複用 image_label_tool 的方式)
                    if hasattr(self.view, 'show_context_menu'):
                        self.view.show_context_menu(event)
                    else:
                        DEBUG("Context menu not implemented in view")

        elif event_type == UIEvent.RESELECT_BT_CLICK:
            DEBUG("Controller: Reselect button clicked.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do RESELECT EVENT")

            try :
                self.select_folders()
            except Exception as e:
                ERROR("Error selecting folders:", e)
                self.view.show_error(e)

        elif event_type == UIEvent.CROP_BT_CLICK:
            DEBUG("Controller: Crop button clicked.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do CROP EVENT")

        elif event_type == UIEvent.ADD_BT_CLICK:
            DEBUG("Controller: Add button clicked.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do ADD EVENT")
            
        elif event_type == UIEvent.CLASS_ID_CHANGE:
            DEBUG("Controller: Class ID changed.")
            DEBUG("entry_label:{}", event_data.get("label"))
            DEBUG("do CLASS ID CHANGE EVENT")

            config_utils.save_class_id_vars(event_data.get("label"))
        elif event_type == UIEvent.MOUSE_LEFT_PRESS:
            x = event_data.get("x", 0)
            y = event_data.get("y", 0)
            supports_resize = event_data.get("supports_resize", False)
            DEBUG("Controller: Mouse left press at ({}, {})", x, y)
            
            # 取得 bbox_controller 從 view
            bbox_controller = getattr(self.view, 'bbox_controller', None)
            if not bbox_controller:
                DEBUG("No bbox_controller found in view")
                return
                
            # 檢查是否在繪製模式
            if bbox_controller.is_in_drawing_mode():
                DEBUG("In drawing mode - start drawing")
                # 繪製模式的原有邏輯保持不變
            else:
                DEBUG("In normal mode - handle selection, dragging, and resizing")
                
                # 使用新的整合滑鼠處理 (複用 plate_box_3.py 的優先序: resize > drag > select)
                if supports_resize and hasattr(bbox_controller, 'handle_mouse_press_with_resize'):
                    operation_type = bbox_controller.handle_mouse_press_with_resize(x, y, self.current_labels)
                    DEBUG("Mouse press operation type: {}", operation_type)
                    
                    if operation_type == "resize":
                        DEBUG("Started resizing")
                        # 觸發視覺更新以顯示 resizing 狀態
                        self.view.draw_labels_on_canvas(self.current_labels)
                        # 更新狀態顯示
                        if hasattr(self.view, 'update_selection_status_display'):
                            resizing_label = bbox_controller.resizing_label
                            self.view.update_selection_status_display(resizing_label)
                    elif operation_type == "drag":
                        DEBUG("Started dragging")
                        # 原有拖拽邏輯保持不變
                    elif operation_type == "select":
                        selected_label = bbox_controller.get_selected_label()
                        DEBUG("Selected label with class_id: {}", selected_label.class_id if selected_label else "None")
                        # 觸發視覺更新
                        self.view.draw_labels_on_canvas(self.current_labels)
                        # 更新狀態顯示
                        if hasattr(self.view, 'update_selection_status_display'):
                            self.view.update_selection_status_display(selected_label)
                    else:  # "none"
                        DEBUG("No operation started")
                        # 更新狀態顯示
                        if hasattr(self.view, 'update_selection_status_display'):
                            self.view.update_selection_status_display(None)
                else:
                    # 回退到原有邏輯 (向後相容)
                    # 首先嘗試開始拖曳 (複用 image_label_tool 的優先序)
                    if bbox_controller.start_drag(x, y, self.current_labels):
                        DEBUG("Started dragging selected label")
                        return
                    
                    # 如果沒有開始拖曳，則處理選擇
                    selected_label = bbox_controller.handle_selection(x, y, self.current_labels)
                    if selected_label:
                        DEBUG("Selected label with class_id: {}", selected_label.class_id)
                        # 觸發視覺更新
                        self.view.draw_labels_on_canvas(self.current_labels)
                        # 更新狀態顯示
                        if hasattr(self.view, 'update_selection_status_display'):
                            self.view.update_selection_status_display(selected_label)
                    else:
                        DEBUG("No label selected")
                        # 更新狀態顯示
                        if hasattr(self.view, 'update_selection_status_display'):
                            self.view.update_selection_status_display(None)
            
        elif event_type == UIEvent.MOUSE_LEFT_RELEASE:
            DEBUG("Controller: Mouse left release.")
            
            # 處理繪製完成
            drawing_result = event_data.get("drawing_result")
            if drawing_result:
                DEBUG("Drawing completed")
                self.handle_new_bbox(drawing_result)
                
            # 處理 resize 完成 (複用 plate_box_3.py 的 resize 完成邏輯)
            resized_label = event_data.get("resized_label")
            if resized_label:
                DEBUG("Resizing completed for label with class_id: {}", resized_label.class_id)
                self.handle_resized_bbox(resized_label)
                
            # 處理拖曳完成 (複用 image_label_tool 的拖曳完成邏輯)
            dragged_label = event_data.get("dragged_label")
            if dragged_label:
                DEBUG("Dragging completed for label with class_id: {}", dragged_label.class_id)
                self.handle_dragged_bbox(dragged_label)
                
        elif event_type == UIEvent.MOUSE_DRAG:
            DEBUG("Controller: Mouse drag.")
            
            # 檢查是否在拖曳或縮放模式中需要重繪 (複用 image_label_tool 的完整重繪策略)
            bbox_controller = getattr(self.view, 'bbox_controller', None)
            if bbox_controller and (bbox_controller.is_dragging or bbox_controller.is_resizing):
                # 使用完整重繪避免殘影 (複用 image_label_tool 的策略 + plate_box_3.py 第 168 行)
                # 立即重繪以避免殘影問題
                self.view.draw_labels_on_canvas(self.current_labels)
            
        elif event_type == UIEvent.DELETE_KEY:
            DEBUG("Controller: Delete key pressed.")
            self.delete_selected_label()

        elif event_type == UIEvent.INPUT_ENTER:
            DEBUG("Controller: Input enter pressed.")
            input_text = event_data.get("text", "")
            DEBUG("Input text:", input_text)
            self.apply_input_text_to_labels(input_text)

    def handle_new_bbox(self, drawing_result):
        """Handle newly drawn bounding box"""
        try:
            yolo_coords = drawing_result['yolo_coords']
            canvas_coords = drawing_result['canvas_coords']
            size = drawing_result['size']
            
            # Create new LabelObject (default class_id=0)
            cx, cy, w_ratio, h_ratio = yolo_coords
            new_label = label_display_utils.LabelObject(0, cx, cy, w_ratio, h_ratio)
            
            # Add to current labels list
            self.current_labels.append(new_label)
            DEBUG("Added new bbox: cx={:.6f}, cy={:.6f}, w={:.6f}, h={:.6f}", cx, cy, w_ratio, h_ratio)
            
            # 重新排序標籤
            if len(self.current_labels) > 1:
                original_count = len(self.current_labels)
                self.current_labels, plate_count = label_display_utils.sort_labels_by_position(self.current_labels)
                DEBUG("Re-sorted {} labels after adding new bbox", original_count)
            
            # Save to label file
            self.save_current_labels()
            
            # Update UI display
            self.update_label_display()
            self.load_label(self.labels_path)  # 更新文字框顯示
            
        except Exception as e:
            ERROR("Error handling new bbox: {}", e)
    
    def handle_dragged_bbox(self, dragged_label):
        """
        處理拖曳完成的 bounding box (複用 image_label_tool 的儲存邏輯)
        
        Args:
            dragged_label (LabelObject): 被拖曳的標籤對象
        """
        try:
            DEBUG("Processing dragged bbox: class_id={}, coords=({:.6f}, {:.6f}, {:.6f}, {:.6f})", 
                  dragged_label.class_id, dragged_label.cx_ratio, 
                  dragged_label.cy_ratio, dragged_label.w_ratio, dragged_label.h_ratio)
            
            # 重新排序標籤（因為位置改變了）
            if len(self.current_labels) > 1:
                original_count = len(self.current_labels)
                self.current_labels, plate_count = label_display_utils.sort_labels_by_position(self.current_labels)
                DEBUG("Re-sorted {} labels after dragging", original_count)
            
            # 儲存更新後的標籤文件
            self.save_current_labels()
            
            # 更新 UI 顯示
            self.update_label_display()
            self.load_label(self.labels_path)  # 更新文字框顯示
            
            DEBUG("Dragged bbox processing completed")
            
        except Exception as e:
            ERROR("Error handling dragged bbox: {}", e)
    
    def handle_resized_bbox(self, resized_label):
        """
        處理 resize 完成的 bounding box (複用 plate_box_3.py 的 resize 處理邏輯)
        
        Args:
            resized_label (LabelObject): 被 resize 的標籤對象
        """
        try:
            DEBUG("Processing resized bbox: class_id={}, coords=({:.6f}, {:.6f}, {:.6f}, {:.6f})", 
                  resized_label.class_id, resized_label.cx_ratio, 
                  resized_label.cy_ratio, resized_label.w_ratio, resized_label.h_ratio)
            
            # 儲存更新後的標籤文件
            self.save_current_labels()
            
            # 更新 UI 顯示
            self.update_label_display()
            
            DEBUG("Resized bbox processing completed")
            
        except Exception as e:
            ERROR("Error handling resized bbox: {}", e)
    
    def save_current_labels(self):
        """Save current labels list to file"""
        if self.image_index < len(self.labels_path):
            label_file_path = self.labels_path[self.image_index]
            
            try:
                with open(label_file_path, 'w', encoding='utf-8') as f:
                    for label in self.current_labels:
                        yolo_line = f"{label.class_id} {label.cx_ratio:.17f} {label.cy_ratio:.17f} {label.w_ratio:.17f} {label.h_ratio:.17f}\n"
                        f.write(yolo_line)
                        
                DEBUG("Saved {} labels to {}", len(self.current_labels), label_file_path)
                
            except Exception as e:
                ERROR("Error saving labels to file: {}", e)
    
    def update_label_display(self):
        """Update label display"""
        # Update label boxes display on canvas
        if self.current_labels:
            self.view.draw_labels_on_canvas(self.current_labels)
        
        # Update text box display
        self.load_label(self.labels_path)
        
    def delete_selected_label(self):
        """刪除選中的標籤"""
        # 取得 bbox_controller 從 view
        bbox_controller = getattr(self.view, 'bbox_controller', None)
        if not bbox_controller:
            DEBUG("No bbox_controller found in view")
            return False
            
        # 獲取選中的標籤
        selected_label = bbox_controller.get_selected_label()
        if not selected_label:
            DEBUG("No label selected for deletion")
            return False
            
        try:
            # 從當前標籤列表中移除
            if selected_label in self.current_labels:
                self.current_labels.remove(selected_label)
                DEBUG("Removed label with class_id: {}", selected_label.class_id)
                
                # 清除選擇狀態
                bbox_controller.clear_selection(self.current_labels)
                
                # 重新排序剩餘的標籤
                if self.current_labels:
                    original_count = len(self.current_labels)
                    self.current_labels, plate_count = label_display_utils.sort_labels_by_position(self.current_labels)
                    DEBUG("Re-sorted {} labels after deletion", original_count)
                
                # 保存更新後的標籤文件
                self.save_current_labels()
                
                # 刷新畫布顯示
                self.update_label_display()
                self.load_label(self.labels_path)  # 更新文字框顯示
                
                # 更新狀態顯示
                if hasattr(self.view, 'update_selection_status_display'):
                    self.view.update_selection_status_display(None)
                
                INFO("Successfully deleted selected label")
                return True
            else:
                ERROR("Selected label not found in current labels list")
                return False
                
        except Exception as e:
            ERROR("Error deleting selected label: {}", e)
            return False
        
    def apply_input_text_to_labels(self, input_text):
        DEBUG("Current labels count : {}", len(self.current_labels))

        class_ids = char_handler.convert_text_to_class_ids(input_text)
        DEBUG("Converted class IDs: {}", class_ids)

        if not char_handler.is_same_length_as_labels(class_ids, len(self.current_labels)):
            self.view.show_error("輸入長度與標籤數量不符，請重新輸入")

            if hasattr(self.view, "clear_input_box"):
                self.view.clear_input_box()
            if hasattr(self.view, "focus_input_box"):
                self.biew.focus_input_box()
                
            return
        
        for i, cid in enumerate(class_ids):
            self.current_labels[i].class_id = cid

        self.save_current_labels()
        self.update_label_display()
