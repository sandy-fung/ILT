from UI_event import UIEvent
import config_utils
import os
from PIL import Image, ImageTk
import cv2

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
        self.images = [
            f for f in os.listdir(self.image_folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        self.images_path = [
            os.path.join(self.image_folder_path, f)
            for f in self.images
        ]

        # load label folder
        self.labels = []
        self.labels_path = []

        for f in self.images:
            label = os.path.splitext(f)[0] + ".txt"
            label_path = os.path.join(self.label_folder_path, label)

            if not os.path.exists(label_path):
                open(label_path, 'w').close() #Create empth txt

            self.labels.append(label)
            self.labels_path.append(label_path)

    def load_image(self, path):
        self.image_index = config_utils.get_image_index()
        DEBUG(f"Get image index: {self.image_index}")
        image = cv2.imread(path[self.image_index])
        if image is None:
            ERROR("Failed to load image at index:", self.image_index)
            return
        DEBUG(f"Image loaded from path: {path[self.image_index]}")

        self.image_height, self.image_width = image.shape[:2]
        DEBUG("Image loaded with height: {}, width: {}", self.image_height, self.image_width)

        config_utils.save_image_info(self.image_height, self.image_width)
        DEBUG("save_image_info to config")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        DEBUG("Image converted to RGB format")

        self.original_image = Image.fromarray(image_rgb)
        DEBUG("Image converted to PIL Image")

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
        DEBUG("Canvasanvas size is zero, using default values size: height: {}, width: {}", canvas_height, canvas_width)

        rs_image = self.original_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(rs_image)
        DEBUG("Image converted to PhotoImage")

        self.view.update_image_canvas(self.image)
        DEBUG("Controller.load_image() completed")
        self.view.update_index_label(self.image_index, self.images_path)

    def load_label(self, path):
        try:
            with open(path[self.image_index], 'r', encoding = 'utf-8') as f:
                content = f.read()
            DEBUG("Label loaded from path:", path[self.image_index])
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


