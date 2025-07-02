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
        self.labels = [
            f for f in os.listdir(self.label_folder_path)
            if f.lower().endswith(('.txt'))
        ]
        self.labels_path = [
            os.path.join(self.label_folder_path, f)
            for f in self.labels
        ]

    def next_image(self):
        DEBUG("Current image index:", self.image_index)
        if self.image_index < len(self.images) - 1:
            self.image_index += 1
        config_utils.save_image_index(self.image_index)

        self.load_image(self.images_path)

    def previous_image(self):
        DEBUG("Current image index:", self.image_index)
        if self.image_index > 0:
            self.image_index -= 1
        config_utils.save_image_index(self.image_index)
        return self.image_index

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
        INFO("save_image_info to config")

        canvas_height, canvas_width = self.view.canvas_height, self.view.canvas_width
        DEBUG("Canvas size: height: {}, width: {}", canvas_height, canvas_width)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        DEBUG("Image converted to RGB format")

        image = Image.fromarray(image).resize((canvas_width, canvas_height))
        DEBUG("Image resized to canvas size: height: {}, width: {}", canvas_height, canvas_width)

        self.image = ImageTk.PhotoImage(image)
        DEBUG("Image converted to PhotoImage")

        self.view.update_image_canvas(self.image)
        DEBUG("Controller.load_image() completed")
        self.view.update_index_label(self.image_index, self.images_path)

    def handle_event(self, event_type, event_data):
        if event_type == UIEvent.WINDOW_READY:
            INFO("Controller: Window is ready.")
            self.load_image(self.images_path)

        elif event_type == UIEvent.LEFT_CTRL_PRESS:
            print("Controller: Left Ctrl pressed.")
            print("entry_value:", event_data.get("value"))
            print("do L-CTRL EVENT")
            self.view.update_text_label("Left Ctrl pressed.")

        elif event_type == UIEvent.RIGHT_CTRL_PRESS:
            print("Controller: Right Ctrl pressed.")
            print("entry_value:", event_data.get("value"))
            print("do R-CTRL EVENT")
            self.view.update_text_label("Right Ctrl pressed.")

        elif event_type == UIEvent.RIGHT_CTRL_RELEASE:
            print("Controller: Right Ctrl released.")
            print("entry_value:", event_data.get("value"))
            print("do R-CTRL RELEASE EVENT")
            self.view.update_text_label("Right Ctrl released.")

        elif event_type == UIEvent.RIGHT_PRESS:
            print("Controller: Right pressed.")
            print("entry_value:", event_data.get("value"))
            print("do R-Press EVENT")
            self.next_image()
            self.view.update_text_label("Right pressed.")

        elif event_type == UIEvent.LEFT_PRESS:
            print("Controller: Left pressed.")
            print("entry_value:", event_data.get("value"))
            print("do L-Press EVENT")
            self.previous_image()
            self.view.update_text_label("Left pressed.")

        elif event_type == UIEvent.MOUSE_LEFT_CLICK:
            print("Controller: Mouse Left clicked.")
            print("entry_value", event_data.get("value"))
            print("do MOUSE-L EVENT")
            self.view.update_text_label("Mouse Left clicked.")

        elif event_type == UIEvent.MOUSE_RIGHT_CLICK:
            print("Controller: Mouse Right clicked.")
            print("entry_value:", event_data.get("value"))
            print("do MOUSE-R EVENT")
            self.view.update_text_label("Mouse Right clicked.")

        elif event_type == UIEvent.RESELECT_BT_CLICK:
            print("Controller: Reselect button clicked.")
            print("entry_value:", event_data.get("value"))
            print("do RESELECT EVENT")

            try :
                self.select_folders()
            except Exception as e:
                ERROR("Error selecting folders:", e)
                self.view.show_error(e)

            self.view.update_text_label("Reselect button clicked.")

        elif event_type == UIEvent.CROP_BT_CLICK:
            print("Controller: Crop button clicked.")
            print("entry_value:", event_data.get("value"))
            print("do CROP EVENT")
            self.view.update_text_label("Crop button clicked.")

        elif event_type == UIEvent.ADD_BT_CLICK:
            print("Controller: Add button clicked.")
            print("entry_value:", event_data.get("value"))
            print("do ADD EVENT")
            self.view.update_text_label("Add button clicked.")


