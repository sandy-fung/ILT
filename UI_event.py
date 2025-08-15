from enum import Enum, auto

class UIEvent(Enum):
    LEFT_CTRL_PRESS = auto()
    RIGHT_CTRL_PRESS = auto()
    RIGHT_CTRL_RELEASE = auto()
    RIGHT_PRESS = auto()
    LEFT_PRESS = auto()

    MOUSE_LEFT_CLICK = auto()
    MOUSE_RIGHT_CLICK = auto()
    MOUSE_LEFT_PRESS = auto()
    MOUSE_LEFT_RELEASE = auto()
    MOUSE_DRAG = auto()

    DRAWING_MODE_TOGGLE = auto()

    DELETE_KEY = auto()
    DELETE_IMAGE = auto()
    MOVE_IMAGE = auto()
    MOVE_IMAGE_CLASSIFIED = auto()

    RESELECT_BT_CLICK = auto()
    CROP_BT_CLICK = auto()
    ADD_BT_CLICK = auto()
    CONFIGURATION_BT_CLICK = auto()
    CLASS_ID_CHANGE = auto()
    INPUT_ENTER = auto()
    
    # Settings dialog events
    SETTINGS_DIALOG_CONFIRM = auto()
    SETTINGS_DIALOG_CANCEL = auto()
    UI_SETTINGS_CHANGED = auto()

    WINDOW_POSITION = auto()
    WINDOW_READY = auto()
    CANVAS_RESIZE = auto()
    TEXT_MODIFIED = auto()
    
    # Magnifier events for preview panel
    MAGNIFIER_SHOW = auto()
    MAGNIFIER_HIDE = auto()
    PREVIEW_DRAG_START = auto()
    PREVIEW_DRAG = auto()
    PREVIEW_DRAG_END = auto()