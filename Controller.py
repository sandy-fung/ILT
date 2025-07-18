from UI_event import UIEvent
import config_utils
import image_utils
import folder_utils
import Words_Label_mapping as wlm
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
        self.image_index = 0
        self.image_width = 0
        self.image_height = 0
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
            self.view.draw_class_id_buttons(config_utils.get_class_id_vars(), wlm.get_labels())

        elif event_type == UIEvent.CANVAS_RESIZE:
            DEBUG("Controller: Canvas resized.")
            self.update_resized_image()

        elif event_type == UIEvent.LEFT_CTRL_PRESS:
            DEBUG("Controller: Left Ctrl pressed.")
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do L-CTRL EVENT")  

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
            DEBUG("entry_value:", event_data.get("value"))
            DEBUG("do MOUSE-R EVENT")

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

