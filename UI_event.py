from enum import Enum, auto

class UIEvent(Enum):
    LEFT_CTRL_PRESS = auto()
    RIGHT_CTRL_PRESS = auto()
    RIGHT_CTRL_RELEASE = auto()
    NEXT_IMAGE = auto()
    PREVIOUS_IMAGE = auto()

    MOUSE_LEFT_CLICK = auto()
    MOUSE_RIGHT_CLICK = auto()
    MOUSE_LEFT_PRESS = auto()
    MOUSE_LEFT_RELEASE = auto()
    MOUSE_DRAG = auto()

    TOGGLE_DRAWING_MODE = auto()

    DELETE_BBOX = auto()
    DELETE_IMAGE = auto()
    MOVE_IMAGE = auto()
    MOVE_IMAGE_CLASSIFIED = auto()
    SEARCH_FILE = auto()
    CUT_IMAGE = auto()
    VERTICAL_LINE_PRESS = auto()

    SELECT_FOLDERS = auto()
    CROP_ALL = auto()
    OPEN_SETTINGS = auto()
    CLASS_ID_CHANGE = auto()
    INPUT_ENTER = auto()
    QUICK_CORRECT = auto()
    BATCH_SORT = auto()
    
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
