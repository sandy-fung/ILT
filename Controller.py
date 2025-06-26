from UI_event import UIEvent
import config_utils
import os

class Controller:
    def __init__(self, view):
        self.view = view

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
            print("No image folder selected.")

        self.label_folder_path = self.view.select_folder("Select Label Folder")
        if not self.label_folder_path:
            print("No label folder selected.")

        self.load_folder()
        

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

        # Save paths to config
        config_utils.save_paths(self.image_folder_path, self.label_folder_path)

    def handle_event(self, event_type, event_data):
        if event_type == UIEvent.LEFT_CTRL_PRESS:
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
            self.view.update_text_label("Right pressed.")

        elif event_type == UIEvent.LEFT_PRESS:
            print("Controller: Left pressed.")
            print("entry_value:", event_data.get("value"))
            print("do L-Press EVENT")
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

    
