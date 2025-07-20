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

    RESELECT_BT_CLICK = auto()
    CROP_BT_CLICK = auto()
    ADD_BT_CLICK = auto()

    WINDOW_READY = auto()
    CANVAS_RESIZE = auto()