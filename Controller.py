from UI_event import UIEvent
import config_utils
import os
from PIL import Image, ImageTk
import cv2

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

    def next_image(self):
        if self.image_index < len(self.images) - 1:
            self.image_index += 1
        config_utils.save_image_index(self.image_index)
        return self.image_index

    def previous_image(self):
        if self.image_index < len(self.images) - 1:
            self.image_index -= 1
        config_utils.save_image_index(self.image_index)
        return self.image_index
        
    def load_image(self, images_path):
        self.image_index = config_utils.get_image_index()
        '''
        if not self.images_path:
            print("No images_path.")
        else:
            print(f"Images_path: {self.images_path}, Image Index: {self.image_index}")
        image = cv2.imread(images_path[self.image_index])
        if image is None:
            print(f"Error: Could not read image at {images_path[self.image_index]}")
            return
        '''
        self.image_height, self.image_width = image.shape[:2]
        #print("3")
        canvas_height, canvas_width = self.view.get_canvas_size()
        config_utils.save_image_info(self.image_width, self.image_height)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image).resize((canvas_width, canvas_height))
        self.tk_image = ImageTk.PhotoImage(image)
        #print("5")
        self.view.update_image_canvas(self.tk_image)

    def handle_event(self, event_type, event_data):
        if event_type == UIEvent.WINDOW_READY:
            print("1")
            self.load_image(self.images_path)
        
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
            self.select_folders()
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

    
