from UI_event import UIEvent
import config_utils
import image_utils
import folder_utils
import label_display_utils
import Words_Label_mapping as wlm
import char_input_handler as char_handler
import os
from log_levels import DEBUG, INFO, ERROR
from image_context import ImageContext
from tkinter import messagebox

DELETE_FILE_TMP_PATH ="delete_tmp"
MOVE_FILE_TMP_PATH ="issue_tmp"
MOVE_FILE_CLASSIFY_PATH ="classified"
CUT_IMAGE_PATH ="cut_tmp"

# Delete mode configuration: "move" (移動到delete資料夾) 或 "delete" (直接刪除)
DELETE_MODE = "move"
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
        self.original_image_for_preview = None
        self.original_image_labels = []  # List of LabelObject instances for original image

        # initial state
        self.drawing_mode = False
        
        # Timer state
        self.timer_active = False
        self.timer_seconds_remaining = 0
        self.timer_id = None
        self.timer_shown_on_startup = False  # Track if timer was shown on startup
        
        # 確保 Timer 設定存在於 config.ini（不覆蓋現有設定）
        config_utils.ensure_timer_config()
        
        # Dragging redraw strategy (複用 image_label_tool 的完整重繪策略)
        self.check_config()


    def check_paths_exist(self):
        if not os.path.exists(self.image_folder_path):
            ERROR("Error: Image folder path does not exist: {}", self.image_folder_path)
            return False
        if not os.path.exists(self.label_folder_path):
            ERROR("Error: Label folder path does not exist: {}", self.label_folder_path)
            return False
        DEBUG("Both paths exist: Image folder path: {}, Label folder path: {}", self.image_folder_path, self.label_folder_path)
        return True

    def check_config(self):

        self.image_folder_path = config_utils.get_image_folder_path()
        self.label_folder_path = config_utils.get_label_folder_path()
        if not self.image_folder_path or not self.label_folder_path:
                self.select_folders()

        else:
            if self.check_paths_exist() is False:
                self.select_folders()

            self.load_folder()


    def select_folders(self):
        # Reset image index
        self.image_index = 0
        config_utils.save_image_index(self.image_index)

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

        # 自動執行批次排序
        self.auto_batch_sort_labels()

        self.load_image(self.images_path)
        
        # Auto-show timer dialog after folder selection if enabled
        self.timer_shown_on_startup = True
        if config_utils.get_timer_enabled():
            self.show_timer_setup_dialog()

    def load_folder(self):
        # load image folder
        self.images, self.images_path = folder_utils.scan_image_folder(self.image_folder_path)

        # load label folder
        self.labels, self.labels_path = folder_utils.scan_label_folder(self.images, self.label_folder_path)

        # Load the current image and labels
        self.image_index = config_utils.get_image_index()
        if self.images_path:
            self.load_image(self.images_path)

    def load_image(self, imgs_path):
        index = config_utils.get_image_index()
        image_path = imgs_path[index]

        self.original_image = image_utils.load_image(image_path)
        
        # Try to load original image for preview if this is a crop
        original_image_path = folder_utils.find_original_image_path(image_path)
        if original_image_path:
            try:
                self.original_image_for_preview = image_utils.load_image(original_image_path)
                DEBUG("Loaded original image for crop preview: {}", original_image_path)
                
                # Try to load original image labels
                original_label_path = folder_utils.find_original_label_path(original_image_path)
                if original_label_path:
                    try:
                        import label_display_utils
                        self.original_image_labels = label_display_utils.parse_label_file(original_label_path)
                        DEBUG("Loaded {} original image labels from: {}", len(self.original_image_labels), original_label_path)
                    except Exception as e:
                        ERROR("Failed to load original image labels: {}", str(e))
                        self.original_image_labels = []
                else:
                    self.original_image_labels = []
                    
            except Exception as e:
                ERROR("Failed to load original image for preview: {}", str(e))
                self.original_image_for_preview = None
                self.original_image_labels = []
        else:
            self.original_image_for_preview = None
            self.original_image_labels = []

        if hasattr(self.view, "bbox_controller"):
            self.view.bbox_controller.clear_selection(self.current_labels)
            DEBUG("Cleared selection in bbox_controller")
            if hasattr(self.view, "update_selection_status_display"):
                self.view.update_selection_status_display(None)

        try:
            W, H = self.original_image.size
            config_utils.save_image_info(H, W)
            self._current_image_size = (W, H)
        except Exception as e:
            ERROR("Failed to update current image info: {}", e)

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

        # Use aspect ratio preserving resize
        resized, actual_rect = image_utils.resize_image_aspect_ratio(
            self.original_image, (canvas_width, canvas_height)
        )

        # Extract actual image area information
        disp_w = actual_rect['width']
        disp_h = actual_rect['height']
        ox = actual_rect['x']
        oy = actual_rect['y']

        W, H = self.original_image.size
        sx = float(disp_w) / float(W) if W else 1.0
        sy = float(disp_h) / float(H) if H else 1.0

        self.image = image_utils.convert_to_tk(resized)

        if hasattr(self.view, "set_image_context"):
            self.view.set_image_context({
                "img_w": W, "img_h": H,
                "disp_w": disp_w, "disp_h": disp_h,
                "ox": ox, "oy": oy,
                "sx": sx, "sy": sy
            })

        self.view.update_image_canvas(self.image)
        
        # Set original image reference in UI for preview functionality
        if hasattr(self.view, 'set_original_image'):
            self.view.set_original_image(self.original_image)
            # Update preview with the full image
            if hasattr(self.view, 'update_preview'):
                self.view.update_preview(self.original_image)
        
        # Set original image labels for preview first
        if hasattr(self.view, 'set_original_image_labels'):
            self.view.set_original_image_labels(self.original_image_labels)
        
        # Set original image for preview if available
        if hasattr(self.view, 'set_original_image_for_preview'):
            self.view.set_original_image_for_preview(self.original_image_for_preview)
        
        DEBUG("Controller.load_image() completed")
        self.view.update_index_label(self.image_index, self.images_path)
        self.view.update_path_label(self.images_path[self.image_index])

        # Parse and draw labels for current image
        self.parse_current_labels()
        if self.current_labels:
            DEBUG("Drawing {} labels on canvas", len(self.current_labels))
            self.view.draw_labels_on_canvas(self.current_labels)

        # save windows size  to default
        window_width, window_height = self.view.get_UI_window_size()
        config_utils.save_window_size(window_width, window_height)

        window_x, window_y = self.view.get_UI_window_position()
        config_utils.save_window_position(window_x, window_y)

    def update_windows_position(self):
        """Update window position based on saved config"""
        # save windows position to default
        window_x, window_y = self.view.get_UI_window_position()
        config_utils.save_window_position(window_x, window_y)

    def load_label(self, path):
        """Load label file and update UI display"""
        try:
            content = folder_utils.load_label(self.labels_path[self.image_index])
            self.view.update_text_box(content)
        except Exception as e:
            ERROR("Error loading label file: {}", e)
            self.view.update_text_box("(Error loading label file)")

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
                # 更新狀態顯示
                if hasattr(self.view, 'update_sorting_status'):
                    self.view.update_sorting_status(original_count, plate_count)
        else:
            self.current_labels = []
            ERROR("Invalid image index for label parsing: {}", self.image_index)

    def handle_text_modified(self):
        try:
            text = self.view.label_text_box.get("1.0", "end").strip()

            labels = label_display_utils.parse_label_text(text)

            labels, plate_count = label_display_utils.sort_labels_by_position(labels)

            self.current_labels = labels
            self.save_current_labels()
            self.update_label_display()

            self.view.update_sorting_status(len(labels), plate_count)

        except Exception as e:
            ERROR("Error handling text modified: {}", e)
    
    def check_if_any_overlaps(self):
        if self.view.label_text_box:
            text = self.view.label_text_box.get("1.0", "end").strip()
        else:
            text = folder_utils.load_label(self.labels_path[self.image_index])
        labels = label_display_utils.parse_label_text(text)   
        if label_display_utils.check_labels_horizontal_overlap(labels) is True:
            self.view.show_error("標籤有重疊，請檢查")
            return True
    
    def on_fresh_image_label(self):
        self.load_image(self.images_path)
        self.load_label(self.labels_path)
        self.parse_current_labels()
        self.check_if_any_overlaps()
        
    def next_image(self):
        DEBUG("Current image index:", self.image_index)
      
        if self.image_index < len(self.images) - 1:
            self.image_index += 1
        else:
            self.view.show_warning(f"Reach the End")
            # 在最後一張時執行自動批次排序
            self.auto_batch_sort_labels()
            return
        config_utils.save_image_index(self.image_index)

        self.on_fresh_image_label()

    def previous_image(self):
        DEBUG("Current image index:", self.image_index)
        if self.image_index > 0:
            self.image_index -= 1
            config_utils.save_image_index(self.image_index)
            self.on_fresh_image_label()
        else:
            # 在第一張時顯示提示並執行自動批次排序
            self.view.show_warning("Reach the Beginning")
            self.auto_batch_sort_labels()
    
    def window_ready(self):
        INFO("Controller: Window is ready.")
        self.on_fresh_image_label()
        self.view.show_class_id_buttons(config_utils.get_class_id_vars(), wlm.get_labels())
        
        # Show timer dialog if not shown yet and timer is enabled (for auto-loaded config case)
        if not self.timer_shown_on_startup and config_utils.get_timer_enabled():
            self.timer_shown_on_startup = True
            self.show_timer_setup_dialog()
        
   #=====  handle_event  ===========
    def handle_event(self, event_type, event_data):
        if event_type == UIEvent.WINDOW_READY:
            self.window_ready()

        elif event_type == UIEvent.CANVAS_RESIZE:
            DEBUG("Controller: Canvas resized.")
            self.update_resized_image()
        elif event_type == UIEvent.WINDOW_POSITION:
            self.update_windows_position()

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
            self.handle_mouse_right_click(event_data)


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
            # DEBUG("entry_value:", event_data.get("value"))
            self.handle_crop_all()

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
            self.handle_mouse_left_press(event_data)

        elif event_type == UIEvent.MOUSE_LEFT_RELEASE:
            DEBUG("Controller: Mouse left release.")
            self.handle_mouse_left_release(event_data)

        elif event_type == UIEvent.MOUSE_DRAG:
            DEBUG("Controller: Mouse drag.")
            self.handle_mouse_drag(event_data)


        elif event_type == UIEvent.DELETE_KEY:
            DEBUG("Controller: Delete key pressed.")
            self.delete_selected_label()

        elif event_type == UIEvent.DELETE_IMAGE:
            DEBUG("Controller: Delete image button pressed.")
            self.move_selected_image_and_label(DELETE_FILE_TMP_PATH)
            
        elif event_type == UIEvent.MOVE_IMAGE:
            DEBUG("Controller: Move image button pressed.")
            plate_type = event_data.get("plate_types", "")
            self.move_selected_image_and_label(MOVE_FILE_TMP_PATH, plate_type)
            
        elif event_type == UIEvent.MOVE_IMAGE_CLASSIFIED:
            DEBUG("Controller: Move image button pressed.")
            plate_type = event_data.get("plate_types", "")
            self.move_selected_image_and_label(MOVE_FILE_CLASSIFY_PATH, plate_type)
            self.view.clear_all_classify_checkbuttons()
            
        elif event_type == UIEvent.SEARCH_FILE:
            DEBUG("Controller: Search file button pressed.")
            search_term = event_data.get("filename", "")
            DEBUG("Search term:", search_term)
            if search_term:
                found_index = folder_utils.search_image_by_filename(self.images, search_term)
                if found_index >= 0:
                    self.image_index = found_index
                    config_utils.save_image_index(self.image_index)
                    self.on_fresh_image_label()
                else:
                    self.view.show_error(f"not found: {search_term}")
            else:
                self.view.show_error("請輸入搜尋關鍵字")
        
        elif event_type == UIEvent.CUT_IMAGE:
            DEBUG("Controller: Cut image button pressed.")
            x_position = event_data.get("position", "")
            # Move the image and label to the cut folder
            self.cut_image_into_two_parts(x_position)
            self.next_image()
           
        elif event_type == UIEvent.VERTICAL_LINE_PRESS:
            DEBUG("Controller: Vertical line pressed")
            # 檢查是否在繪框模式
            if self.view.bbox_controller and self.view.bbox_controller.is_in_drawing_mode():
                # 退出繪框模式
                self.view.bbox_controller.toggle_drawing_mode()
                self.view.update_drawing_mode_display()
                DEBUG("Exited drawing mode due to vertical line press")
            

        elif event_type == UIEvent.INPUT_ENTER:
            DEBUG("Controller: Input enter pressed.")
            input_text = event_data.get("text", "")
            DEBUG("Input text:", input_text)
            self.apply_input_text_to_labels(input_text)
            
        elif event_type == UIEvent.SELECT_LEFTMOST_BBOX:
            DEBUG("Controller: Select leftmost bbox clicked.")
            self.select_leftmost_bbox_and_trigger_input()
            
        elif event_type == UIEvent.CONFIGURATION_BT_CLICK:
            DEBUG("Controller: Configuration button clicked.")
            self.handle_configuration_button()
            
        elif event_type == UIEvent.BATCH_SORT:
            DEBUG("Controller: Batch sort button clicked.")
            self.batch_sort_all_labels()
            
        elif event_type == UIEvent.SETTINGS_DIALOG_CONFIRM:
            DEBUG("Controller: Settings dialog confirmed.")
            self.handle_settings_confirm(event_data)
            
        elif event_type == UIEvent.UI_SETTINGS_CHANGED:
            DEBUG("Controller: UI settings changed.")
            self.handle_ui_settings_change(event_data)

        elif event_type == UIEvent.TEXT_MODIFIED:
            self.handle_text_modified()

    def update_label_view(self, label):
        if hasattr(self.view, 'update_selection_status_display'):
            self.view.update_selection_status_display(label)

    def handle_crop_all(self):
        import crop_helper
        crop_helper.start_cropping(self.image_folder_path, self.images_path, self.labels_path)
        
        
    def handle_mouse_right_click(self, event_data):
        event = event_data.get("value")
        DEBUG("Right click at ({}, {})", event.x, event.y)
        # 取得 bbox_controller 從 view
        bbox_controller = getattr(self.view, 'bbox_controller', None)
        if bbox_controller and bbox_controller.get_selected_label():
            # 如果有選中的標籤，檢查右鍵是否點擊在選中的標籤上
            selected_label = bbox_controller.get_selected_label()
            # 使用已修正的 _label_contains_point 方法，它會正確處理黑邊偏移
            if bbox_controller._label_contains_point(selected_label, event.x, event.y):
                # 顯示右鍵菜單
                if hasattr(self.view, 'show_context_menu'):
                    self.view.show_context_menu(event)
                else:
                    DEBUG("Context menu not implemented in view")


    def handle_mouse_left_press(self, event_data):
        x = event_data.get("x", 0)
        y = event_data.get("y", 0)
        supports_resize = event_data.get("supports_resize", False)
        DEBUG("Controller: Mouse left press at ({}, {})", x, y)
        # 取得 bbox_controller 從 view
        bbox_controller = getattr(self.view, 'bbox_controller', None)
        # 取得 bbox_controller 從 view
        if not bbox_controller:
            DEBUG("No bbox_controller found in view")
            return
        # 檢查是否在繪製模式
        if bbox_controller.is_in_drawing_mode():
            DEBUG("In drawing mode - start drawing")
            # Handle drawing mode
        else:
            DEBUG("In normal mode - handle selection, dragging, and resizing")
            # Handle operations in priority order: resize > drag > select
            if supports_resize and hasattr(bbox_controller, 'handle_mouse_press_with_resize'):
                operation_type = bbox_controller.handle_mouse_press_with_resize(x, y, self.current_labels)
                DEBUG("Mouse press operation type: {}", operation_type)
                self._handle_operation_type(operation_type, bbox_controller)
            else:
                # Fallback to standard selection handling
                # Try to start dragging
                if bbox_controller.start_drag(x, y, self.current_labels):
                    DEBUG("Started dragging selected label")
                    return
            self._handle_selection(bbox_controller, x, y)



    def _handle_operation_type(self, operation_type, bbox_controller):
            if operation_type == "resize":
                DEBUG("Started resizing")
                # 觸發視覺更新以顯示 resizing 狀態
                self.view.draw_labels_on_canvas(self.current_labels)
                # 更新狀態顯示
                resizing_label = bbox_controller.resizing_label
                self.update_label_view(resizing_label)

            elif operation_type == "drag":
                    DEBUG("Started dragging")
                    # Handle dragging operation
            elif operation_type == "select":
                    selected_label = bbox_controller.get_selected_label()
                    DEBUG("Selected label with class_id: {}", selected_label.class_id if selected_label else "None")
                    # 觸發視覺更新
                    self.view.draw_labels_on_canvas(self.current_labels)
                    # 更新狀態顯示
                    self.update_label_view(selected_label)

            else:  # "none"
                    DEBUG("No operation started")
                    # 更新狀態顯示
                    self.update_label_view(None)

    def _handle_selection(self, bbox_controller, x, y):
             # Handle selection if dragging didn't start
            selected_label = bbox_controller.handle_selection(x, y, self.current_labels)
            self.view.draw_labels_on_canvas(self.current_labels)
   
            if selected_label:
                DEBUG("Selected label with class_id: {}", selected_label.class_id)
                # 觸發視覺更新
                self.view.draw_labels_on_canvas(self.current_labels)
                # 更新狀態顯示
                self.update_label_view(selected_label)
                self.view.highlight_yolo_line_for_label(selected_label)

            else:
                DEBUG("No label selected")
                # 更新狀態顯示
                self.update_label_view(None)
                self.view.highlight_yolo_line_for_label(None)

    def handle_mouse_left_release(self, event_data):
            # 處理繪製完成
            drawing_result = event_data.get("drawing_result")
            class_id = event_data.get("class_id")
            if drawing_result:
                DEBUG("Drawing completed")
                self.handle_new_bbox(drawing_result, class_id)

            # 處理 resize 完成
            resized_label = event_data.get("resized_label")
            if resized_label:
                DEBUG("Resizing completed for label with class_id: {}", resized_label.class_id)
                self.handle_resized_bbox(resized_label)

            # 處理拖曳完成
            dragged_label = event_data.get("dragged_label")
            if dragged_label:
                DEBUG("Dragging completed for label with class_id: {}", dragged_label.class_id)
                self.handle_dragged_bbox(dragged_label)

    def handle_mouse_drag(self, event_data):
            # 檢查是否在拖曳或縮放模式中需要重繪
            bbox_controller = getattr(self.view, 'bbox_controller', None)
            if bbox_controller and (bbox_controller.is_dragging or bbox_controller.is_resizing):
                # Redraw to prevent visual artifacts
                self.view.draw_labels_on_canvas(self.current_labels)

    def handle_new_bbox(self, drawing_result, class_id):
        """Handle newly drawn bounding box"""
        try:
            yolo_coords = drawing_result['yolo_coords']
            canvas_coords = drawing_result['canvas_coords']
            size = drawing_result['size']

            # Create new LabelObject (default class_id=0)
            cx, cy, w_ratio, h_ratio = yolo_coords
            new_label = label_display_utils.LabelObject(class_id, cx, cy, w_ratio, h_ratio)

            # Add to current labels list
            self.current_labels.append(new_label)
            DEBUG("Added new bbox: cx={:.6f}, cy={:.6f}, w={:.6f}, h={:.6f}", cx, cy, w_ratio, h_ratio)

            # 重新排序標籤
            if len(self.current_labels) > 1:
                original_count = len(self.current_labels)
                self.current_labels, plate_count = label_display_utils.sort_labels_by_position(self.current_labels)
                DEBUG("Re-sorted {} labels after adding new bbox", original_count)
            self.refresh()

        except Exception as e:
            ERROR("Error handling new bbox: {}", e)

    def handle_dragged_bbox(self, dragged_label):
        """
        處理拖曳完成的 bounding box
        
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

            self.refresh()

            DEBUG("Dragged bbox processing completed")

        except Exception as e:
            ERROR("Error handling dragged bbox: {}", e)

    def handle_resized_bbox(self, resized_label):
        """
        處理 resize 完成的 bounding box
        
        Args:
            resized_label (LabelObject): 被 resize 的標籤對象
        """
        try:
            DEBUG("Processing resized bbox: class_id={}, coords=({:.6f}, {:.6f}, {:.6f}, {:.6f})",
                  resized_label.class_id, resized_label.cx_ratio,
                  resized_label.cy_ratio, resized_label.w_ratio, resized_label.h_ratio)

            self.refresh()

            DEBUG("Resized bbox processing completed")

        except Exception as e:
            ERROR("Error handling resized bbox: {}", e)

    def refresh(self):
        # 保存更新後的標籤文件
        self.save_current_labels()

        # 刷新畫布顯示
        self.update_label_display()
        # 更新文字框顯示
        self.load_label(self.labels_path)

    def save_current_labels(self):
        """Save current labels list to file"""
        if self.image_index < len(self.labels_path):
            label_file_path = self.labels_path[self.image_index]

            try:
                # Ensure label directory exists
                os.makedirs(os.path.dirname(label_file_path), exist_ok=True)
                
                if not self.current_labels:
                    auto_create = config_utils.get_auto_create_labels()
                    if auto_create:
                        with open(label_file_path, 'w', encoding='utf-8') as f:
                            pass
                        DEBUG("Created empty label file: {}", label_file_path)
                    else:
                        if os.path.exists(label_file_path):
                            os.remove(label_file_path)
                            DEBUG("Removed empty label file: {}", label_file_path)
                else:
                    with open(label_file_path, 'w', encoding='utf-8') as f:
                        for label in self.current_labels:
                            yolo_line = f"{label.class_id} {label.cx_ratio:.17f} {label.cy_ratio:.17f} {label.w_ratio:.17f} {label.h_ratio:.17f}\n"
                            f.write(yolo_line)
                    DEBUG("Saved {} labels to {}", len(self.current_labels), label_file_path)

            except PermissionError as e:
                ERROR("Permission denied when saving label file {}: {}", label_file_path, e)
                self.view.show_error(f"Permission denied saving label file\n{label_file_path}")
            except OSError as e:
                ERROR("OS error when saving label file {}: {}", label_file_path, e)
                self.view.show_error(f"OS error saving label file\n{e}")
            except Exception as e:
                ERROR("Unexpected error saving labels to file {}: {}", label_file_path, e)
                self.view.show_error(f"Error saving label file\n{e}")

    def batch_sort_all_labels(self):
        """批次排序目錄下所有標籤檔案"""
        if not self.label_folder_path or not os.path.exists(self.label_folder_path):
            self.view.show_error("標籤資料夾路徑無效")
            return
        
        try:
            # 掃描標籤資料夾中的所有 .txt 檔案
            label_files = [f for f in os.listdir(self.label_folder_path) if f.lower().endswith('.txt')]
            
            if not label_files:
                self.view.show_warning("標籤資料夾中未找到任何 .txt 檔案")
                return
            
            # 顯示確認對話框
            from tkinter import messagebox
            result = messagebox.askyesno(
                "批次排序確認", 
                f"即將對 {len(label_files)} 個標籤檔案進行排序\n"
                "此操作會修改檔案內容，是否繼續？"
            )
            
            if not result:
                return
            
            processed_count = 0
            sorted_count = 0
            error_count = 0
            
            INFO("開始批次排序 {} 個標籤檔案", len(label_files))
            
            for label_file in label_files:
                label_file_path = os.path.join(self.label_folder_path, label_file)
                
                try:
                    # 解析標籤檔案
                    labels = label_display_utils.parse_label_file(label_file_path)
                    
                    if not labels:
                        DEBUG("跳過空白標籤檔案: {}", label_file)
                        processed_count += 1
                        continue
                    
                    # 記錄排序前的標籤數量
                    original_count = len(labels)
                    
                    # 執行排序
                    sorted_labels, plate_count = label_display_utils.sort_labels_by_position(labels)
                    
                    # 將排序後的標籤寫回檔案
                    with open(label_file_path, 'w', encoding='utf-8') as f:
                        for label in sorted_labels:
                            yolo_line = f"{label.class_id} {label.cx_ratio:.17f} {label.cy_ratio:.17f} {label.w_ratio:.17f} {label.h_ratio:.17f}\n"
                            f.write(yolo_line)
                    
                    DEBUG("已排序檔案 {}: {} 個標籤, {} 個車牌", label_file, original_count, plate_count)
                    processed_count += 1
                    sorted_count += 1
                    
                except Exception as e:
                    ERROR("處理檔案 {} 時發生錯誤: {}", label_file, e)
                    error_count += 1
                    processed_count += 1
            
            # 顯示處理結果
            result_message = f"批次排序完成！\n"
            result_message += f"處理檔案: {processed_count}/{len(label_files)}\n"
            result_message += f"成功排序: {sorted_count}\n"
            
            if error_count > 0:
                result_message += f"發生錯誤: {error_count}"
                self.view.show_warning(result_message)
            else:
                self.view.show_warning(result_message)
            
            # 重新載入當前標籤以反映變更
            if self.image_index < len(self.labels_path):
                self.parse_current_labels()
                self.update_label_display()
            
            INFO("批次排序完成: {}/{} 檔案成功處理", sorted_count, len(label_files))
            
        except Exception as e:
            ERROR("批次排序過程中發生錯誤: {}", e)
            self.view.show_error(f"批次排序失敗: {e}")

    def auto_batch_sort_labels(self):
        """自動批次排序目錄下所有標籤檔案（無確認對話框）"""
        if not self.label_folder_path or not os.path.exists(self.label_folder_path):
            DEBUG("標籤資料夾路徑無效，跳過自動排序")
            return
        
        try:
            # 掃描標籤資料夾中的所有 .txt 檔案
            label_files = [f for f in os.listdir(self.label_folder_path) if f.lower().endswith('.txt')]
            
            if not label_files:
                INFO("標籤資料夾中未找到任何 .txt 檔案，跳過自動排序")
                return
            
            processed_count = 0
            sorted_count = 0
            error_count = 0
            
            INFO("開始自動批次排序 {} 個標籤檔案", len(label_files))
            
            for label_file in label_files:
                label_file_path = os.path.join(self.label_folder_path, label_file)
                
                try:
                    # 解析標籤檔案
                    labels = label_display_utils.parse_label_file(label_file_path)
                    
                    if not labels:
                        DEBUG("跳過空白標籤檔案: {}", label_file)
                        processed_count += 1
                        continue
                    
                    # 記錄排序前的標籤數量
                    original_count = len(labels)
                    
                    # 執行排序
                    sorted_labels, plate_count = label_display_utils.sort_labels_by_position(labels)
                    
                    # 將排序後的標籤寫回檔案
                    with open(label_file_path, 'w', encoding='utf-8') as f:
                        for label in sorted_labels:
                            yolo_line = f"{label.class_id} {label.cx_ratio:.17f} {label.cy_ratio:.17f} {label.w_ratio:.17f} {label.h_ratio:.17f}\n"
                            f.write(yolo_line)
                    
                    DEBUG("已自動排序檔案 {}: {} 個標籤, {} 個車牌", label_file, original_count, plate_count)
                    processed_count += 1
                    sorted_count += 1
                    
                except Exception as e:
                    ERROR("自動處理檔案 {} 時發生錯誤: {}", label_file, e)
                    error_count += 1
                    processed_count += 1
            
            # 顯示處理結果
            result_message = f"自動批次排序完成！\n"
            result_message += f"處理檔案: {processed_count}/{len(label_files)}\n"
            result_message += f"成功排序: {sorted_count}\n"
            
            if error_count > 0:
                result_message += f"發生錯誤: {error_count}"
                self.view.show_warning(result_message)
            else:
                INFO("自動批次排序完成: {}/{} 檔案成功處理", sorted_count, len(label_files))
                # 成功時不顯示對話框，只記錄日誌
            
            # 重新載入當前標籤以反映變更
            if self.image_index < len(self.labels_path):
                self.parse_current_labels()
                self.update_label_display()
            
        except Exception as e:
            ERROR("自動批次排序過程中發生錯誤: {}", e)
            self.view.show_error(f"自動批次排序失敗: {e}")

    def update_label_display(self):
        """Update label display"""
        # Update label boxes display on canvas
        if self.current_labels:
            self.view.draw_labels_on_canvas(self.current_labels)
        else:
            self.view.clear_all_labels_canvas()

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

                self.refresh()

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
        
    def select_leftmost_bbox_and_trigger_input(self):
        """Select the leftmost bbox and trigger input enter event"""
        if not self.current_labels:
            DEBUG("No labels to select")
            return
            
        bbox_ctrl = self.view.bbox_controller
        if not bbox_ctrl:
            DEBUG("No bbox controller available")
            return
            
        # Find leftmost label (minimum cx_ratio)
        leftmost_label = min(self.current_labels, key=lambda label: label.cx_ratio)
        DEBUG("Found leftmost label with cx_ratio: {}", leftmost_label.cx_ratio)
        
        # Clear current selection
        bbox_ctrl.clear_selection(self.current_labels)
        
        # Select the leftmost label
        leftmost_label.set_selected(True)
        bbox_ctrl.selected_label = leftmost_label
        
        # Update display
        self.update_label_display()
        self.view.update_selection_status_display(leftmost_label)
        
        # Get text from input box and trigger input enter
        if self.view.input_box:
            input_text = self.view.input_box.get().strip()
            if input_text and input_text != "請輸入車牌號碼":
                DEBUG("Triggering input enter with text: {}", input_text)
                self.apply_input_text_to_labels(input_text)
                self.view.window.focus_set()
            else:
                DEBUG("Input box is empty or has placeholder text")
        else:
            DEBUG("Input box not available")
    
    def apply_input_text_to_labels(self, input_text):
        DEBUG("Current labels count : {}", len(self.current_labels))

        class_ids = char_handler.convert_text_to_class_ids(input_text)
        DEBUG("Converted class IDs: {}", class_ids)

        bbox_ctrl = self.view.bbox_controller
        selected_label = bbox_ctrl.get_selected_label() if bbox_ctrl else None

        if selected_label:
            try:
                start_idx = self.current_labels.index(selected_label)
                DEBUG("Selected label found at index: {}", start_idx)

                if len(class_ids) > len(self.current_labels) - start_idx:
                    self.view.show_error("輸入長度超過剩餘標籤數量，請重新輸入")
                    ERROR("Input length exceeds remaining labels count. Input: {}, Remaining: {}", len(class_ids), len(self.current_labels) - start_idx)
                    return
                
                for i, cid in enumerate(class_ids):
                    self.current_labels[start_idx + i].class_id = cid

                    self.save_current_labels()
                    self.update_label_display()

                # Add to plate memory after successful application
                if hasattr(self.view, 'add_plate_to_memory_from_controller'):
                    self.view.add_plate_to_memory_from_controller(input_text)

                return

            except ValueError:
                self.view.show_error()
                ERROR("Selected label not found in current labels list")
                return


        if not char_handler.is_same_length_as_labels(class_ids, len(self.current_labels)):
            self.view.show_error("輸入長度與標籤數量不符，請重新輸入")
            
            if hasattr(self.view, "focus_input_box"):
                self.view.focus_input_box()
                
            return
        
        for i, cid in enumerate(class_ids):
            self.current_labels[i].class_id = cid

        self.save_current_labels()
        self.update_label_display()

        # Add to plate memory after successful application
        if hasattr(self.view, 'add_plate_to_memory_from_controller'):
            self.view.add_plate_to_memory_from_controller(input_text)

    def move_selected_image_and_label(self, destination, plate_type=None): 
        if self.image_index < len(self.images_path):
            image_path = self.images_path[self.image_index]
            label_path = self.labels_path[self.image_index]
            # Remove image and label files
            dest_folder_path = os.path.join(self.image_folder_path, destination)
            DEBUG(f"move to folder:{dest_folder_path}")
            if not os.path.exists(dest_folder_path):
                os.makedirs(dest_folder_path)
            
            try:
                INFO("Deleted image: {} and label: {}", image_path, label_path)
                if plate_type is not None:
                    if isinstance(plate_type, list):
                        plate_type_str = "_".join(plate_type)
                    else:
                        plate_type_str = plate_type  # 原本就是字串
                    # plate_type_str = "_".join(plate_type)
                    base_name, ext = os.path.splitext(os.path.basename(image_path))
                    new_image_name = f"{plate_type_str}_{base_name}{ext}"
                    new_label_name = f"{plate_type_str}_{os.path.basename(label_path)}"
                    new_image_path = os.path.join(dest_folder_path, new_image_name)
                    new_label_path = os.path.join(dest_folder_path, new_label_name)
                else:
                    new_image_path = os.path.join(dest_folder_path, os.path.basename(image_path))
                    new_label_path = os.path.join(dest_folder_path, os.path.basename(label_path))
                    
                # Move and rename the files using the new deletion handling
                if destination == DELETE_FILE_TMP_PATH:
                    # 使用新的delete處理機制
                    folder_utils.handle_file_deletion(image_path, DELETE_MODE, new_image_path)
                    folder_utils.handle_file_deletion(label_path, DELETE_MODE, new_label_path)
                    
                    # 檢查是否為crop圖片，如果是則檢查是否需要處理原始圖片
                    self._handle_crop_deletion_check(image_path)
                else:
                    # 非delete操作，保持原有邏輯
                    folder_utils.move_file(image_path, new_image_path)
                    folder_utils.move_file(label_path, new_label_path)
                
            except Exception as e:
                ERROR("Error processing image or label file: {}", e)
               
            # Remove from lists
            del self.images_path[self.image_index]
            del self.labels_path[self.image_index]
            del self.images[self.image_index]
            del self.labels[self.image_index]
            # Adjust index
            if self.image_index >= len(self.images_path):
                self.image_index = max(0, len(self.images_path) - 1)
            config_utils.save_image_index(self.image_index)
            

            # # Reload image and labels
            try:
                if len(self.images_path) == 0:
                    self.view.show_warning(f"Folder of images is empty now")
                    # clear everything on canvas and text_view
                    self.view.clear_all_labels_canvas()
                    self.view.update_image_canvas()
                    self.view.update_text_box()
                    return
 
                self.on_fresh_image_label()
            except Exception as e:
                ERROR("Error reloading image or label after deletion: {}", e)
                self.view.show_error(f"Error reloading image or label: {e}")

               
        else:
                ERROR("No image to delete at index: {}", self.image_index)

    def _handle_crop_deletion_check(self, crop_image_path: str):
        """
        檢查crop圖片刪除後是否需要處理原始圖片
        
        Args:
            crop_image_path: 被刪除的crop圖片路徑
        """
        try:
            crop_filename = os.path.basename(crop_image_path)
            crop_stem = os.path.splitext(crop_filename)[0]
            
            # 檢查是否為crop圖片
            if "_crop_" not in crop_stem:
                DEBUG("Not a crop image, skipping original image check: {}", crop_image_path)
                return
            
            # 取得原始檔案名稱
            original_stem = folder_utils.get_original_filename_from_crop(crop_stem)
            
            # 檢查是否所有crop都在delete資料夾
            if folder_utils.are_all_crops_in_delete_folder(original_stem, self.image_folder_path, DELETE_FILE_TMP_PATH):
                DEBUG("All crops deleted for original: {}, processing original image", original_stem)
                
                # 找到原始圖片路徑
                original_image_path = folder_utils.find_original_image_path(crop_image_path)
                if not original_image_path:
                    DEBUG("Original image not found for crop: {}", crop_image_path)
                    return
                
                # 找到原始標註檔路徑
                original_label_path = folder_utils.find_original_label_path(original_image_path)
                
                # 準備目標路徑
                delete_folder_path = os.path.join(self.image_folder_path, DELETE_FILE_TMP_PATH)
                original_image_filename = os.path.basename(original_image_path)
                original_label_filename = os.path.basename(original_label_path) if original_label_path else ""
                
                dest_image_path = os.path.join(delete_folder_path, original_image_filename)
                dest_label_path = os.path.join(delete_folder_path, original_label_filename) if original_label_filename else None
                
                # 處理原始圖片和標註檔
                folder_utils.handle_file_deletion(original_image_path, DELETE_MODE, dest_image_path)
                if original_label_path and dest_label_path:
                    folder_utils.handle_file_deletion(original_label_path, DELETE_MODE, dest_label_path)
                
                INFO("Processed original image and label for deleted crops: {}", original_image_path)
            else:
                DEBUG("Not all crops deleted yet for original: {}", original_stem)
                
        except Exception as e:
            ERROR("Error in crop deletion check: {}", e)

    def cut_image_into_two_parts(self, x_position):
        from cut_image_util import split_image_and_labels
        canvas_height, canvas_width = self.view.get_canvas_size()
        dest_folder_path = os.path.join(self.image_folder_path, CUT_IMAGE_PATH)
        split_image_and_labels(
            self.images_path[self.image_index],
            self.labels_path[self.image_index],
            x_position,
            canvas_width,
            dest_folder_path
        )
        
    def handle_configuration_button(self):
        """Handle configuration button click"""
        try:
            current_settings = self.get_current_ui_settings()
            DEBUG("Opening settings dialog with current settings: {}", current_settings)
            if hasattr(self.view, 'show_settings_dialog'):
                self.view.show_settings_dialog(current_settings, self.on_settings_confirm)
            else:
                ERROR("Settings dialog not implemented in view")
        except Exception as e:
            ERROR("Error handling configuration button: {}", e)
    
    def show_timer_setup_dialog(self):
        """Show timer setup dialog and start timer if confirmed"""
        try:
            from timer_dialog import TimerSetupDialog
            
            # Get timer default minutes from config
            default_minutes = config_utils.get_timer_default_minutes()
            if default_minutes is None:
                default_minutes = 10  # Default to 10 minute
            
            # Create and show timer dialog
            timer_dialog = TimerSetupDialog(self.view.window, default_minutes)
            minutes = timer_dialog.show()
            
            if minutes is not None:
                # Start timer with selected minutes
                self.start_timer(minutes)
                
        except Exception as e:
            ERROR("Error showing timer setup dialog: {}", e)
    
    def start_timer(self, minutes):
        """Start the countdown timer"""
        try:
            self.timer_seconds_remaining = minutes * 60
            self.timer_active = True
            
            # Start countdown
            self.update_timer()
            
            INFO("Timer started for {} minutes", minutes)
            
            # Save timer settings to config
            config_utils.save_timer_settings(default_minutes=minutes)
            
        except Exception as e:
            ERROR("Error starting timer: {}", e)
    
    def update_timer(self):
        """Update the timer countdown"""
        if self.timer_active and self.timer_seconds_remaining > 0:
            # Update display
            minutes = self.timer_seconds_remaining // 60
            seconds = self.timer_seconds_remaining % 60
            time_text = f"{minutes:02d}:{seconds:02d}"
            
            # Determine color based on remaining time
            if self.timer_seconds_remaining <= 60:
                color = "red"
            elif self.timer_seconds_remaining <= 180:
                color = "orange"
            else:
                color = "blue"
            
            # Update timer display
            if hasattr(self.view, 'update_timer_display'):
                self.view.update_timer_display(time_text, color)
            
            # Decrement timer
            self.timer_seconds_remaining -= 1
            
            # Schedule next update
            self.timer_id = self.view.window.after(1000, self.update_timer)
            
        elif self.timer_active and self.timer_seconds_remaining == 0:
            # Timer finished
            self.timer_finished()
    
    def stop_timer(self):
        """Stop the countdown timer"""
        try:
            self.timer_active = False
            
            # Cancel scheduled update
            if self.timer_id:
                self.view.window.after_cancel(self.timer_id)
                self.timer_id = None
            
            # Clear timer display
            if hasattr(self.view, 'update_timer_display'):
                self.view.update_timer_display("", "blue")
            
            INFO("Timer stopped")
            
        except Exception as e:
            ERROR("Error stopping timer: {}", e)
    
    def timer_finished(self):
        """Handle timer finished event"""
        try:
            self.timer_active = False
            
            # Clear timer display
            if hasattr(self.view, 'update_timer_display'):
                self.view.update_timer_display("時間到！", "red")
            
            # Show notification
            messagebox.showinfo(
                "休息時間", 
                "標註時間到了！\n請休息一下，保護眼睛！",
                parent=self.view.window
            )
            
            # Clear display after notification
            if hasattr(self.view, 'update_timer_display'):
                self.view.update_timer_display("", "blue")
            
            INFO("Timer finished - notification shown")
            
            # Auto-restart timer setup after break if enabled
            if config_utils.get_timer_enabled():
                self.show_timer_setup_dialog()
            
        except Exception as e:
            ERROR("Error handling timer finished: {}", e)
    
    def handle_settings_confirm(self, event_data):
        """Handle settings dialog confirmation"""
        try:
            settings = event_data.get("settings", {})
            DEBUG("Applying new UI settings: {}", settings)
            
            # Save UI settings
            config_utils.save_ui_settings(**settings)
            
            # Apply settings to UI
            if hasattr(self.view, 'apply_ui_settings'):
                self.view.apply_ui_settings(settings)
            
            INFO("UI settings updated successfully")

            self.update_label_display()
        except Exception as e:
            ERROR("Error handling settings confirmation: {}", e)
    
    def handle_ui_settings_change(self, event_data):
        """Handle UI settings change"""
        try:
            settings = event_data.get("settings", {})
            DEBUG("UI settings changed: {}", settings)
            
            # Apply settings immediately
            if hasattr(self.view, 'apply_ui_settings'):
                self.view.apply_ui_settings(settings)
                
        except Exception as e:
            ERROR("Error handling UI settings change: {}", e)
    
    def get_current_ui_settings(self):
        """Get current UI settings"""
        return config_utils.get_all_ui_settings()
    
    def on_settings_confirm(self, settings):
        """Callback for settings confirmation"""
        self.handle_event(UIEvent.SETTINGS_DIALOG_CONFIRM, {"settings": settings})
        
