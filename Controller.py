from UI_event import UIEvent

class Controller():
    def __init__(self, view):
        self.view = view
    
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