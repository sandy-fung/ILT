from configparser import ConfigParser
from log_levels import ERROR

DEFAULT_CONFI_PATH = "config.ini"

config = ConfigParser()
config.read(DEFAULT_CONFI_PATH)

def get_image_folder_path():
    try:
        return config.get("Path", "image_folder_path")
    except:
        return None

def get_label_folder_path():
    try:
        return config.get("Path", "label_folder_path")
    except:
        return None

def save_paths(image_folder_path, label_folder_path):
    if not config.has_section("Path"):
        config.add_section("Path")
    config.set("Path", "image_folder_path", image_folder_path)
    config.set("Path", "label_folder_path", label_folder_path)

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)


def get_class_id_vars():
    try:
        return config.get("Path", "class_id_vars")
    except:
        return None
    
def save_class_id_vars(class_id_vars):
    if not config.has_section("Path"):
        config.add_section("Path")
    config.set("Path", "class_id_vars", class_id_vars)

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)


def get_image_index():
    try:
        return config.getint("Path", "image_index")
    except:
        return 0

def save_image_index(index):
    if not config.has_section("Path"):
        config.add_section("Path")
    config.set("Path", "image_index", str(index))

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)


def get_image_info():
    try:
        height = config.getint("ImageInfo", "image_height")
        width = config.getint("ImageInfo", "image_width")
        return height, width
    except:
        return 640, 640

def save_image_info(height, width):
    if not config.has_section("ImageInfo"):
        config.add_section("ImageInfo")
    config.set("ImageInfo", "image_height", str(height))
    config.set("ImageInfo", "image_width", str(width))
    
    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)


# Magnifier configuration functions
def get_magnifier_enabled():
    """Get whether magnifier is enabled"""
    try:
        return config.getboolean("preview_magnifier", "enabled")
    except:
        return True  # Default to enabled

def get_magnifier_zoom_factor():
    """Get magnifier zoom factor"""
    try:
        return config.getfloat("preview_magnifier", "zoom_factor")
    except:
        return 3.0  # Default 3x zoom

def get_magnifier_tooltip_size():
    """Get magnifier tooltip size"""
    try:
        return config.getint("preview_magnifier", "tooltip_size")
    except:
        return 200  # Default tooltip size

def get_magnifier_cursor_type():
    """Get magnifier cursor type"""
    try:
        return config.get("preview_magnifier", "cursor_type")
    except:
        return "target"  # Default cursor - target/crosshair looks more like magnifier

def get_magnifier_region_size():
    """Get magnifier region extraction size"""
    try:
        return config.getint("preview_magnifier", "region_size")
    except:
        return 50  # Default region size

def get_magnifier_cache_size():
    """Get magnifier cache size"""
    try:
        return config.getint("preview_magnifier", "cache_size")
    except:
        return 10  # Default cache size

def save_magnifier_config(enabled=None, zoom_factor=None, tooltip_size=None, 
                         cursor_type=None, region_size=None, cache_size=None):
    """Save magnifier configuration settings"""
    if not config.has_section("preview_magnifier"):
        config.add_section("preview_magnifier")
    
    if enabled is not None:
        config.set("preview_magnifier", "enabled", str(enabled).lower())
    if zoom_factor is not None:
        config.set("preview_magnifier", "zoom_factor", str(zoom_factor))
    if tooltip_size is not None:
        config.set("preview_magnifier", "tooltip_size", str(tooltip_size))
    if cursor_type is not None:
        config.set("preview_magnifier", "cursor_type", cursor_type)
    if region_size is not None:
        config.set("preview_magnifier", "region_size", str(region_size))
    if cache_size is not None:
        config.set("preview_magnifier", "cache_size", str(cache_size))

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)


# Label file configuration functions
def get_auto_create_labels():
    """Get whether to automatically create empty label files"""
    try:
        return config.getboolean("LabelFiles", "auto_create_labels")
    except:
        return False  # Default to False (lazy creation like ../image_label_tool)

def set_auto_create_labels(enabled):
    """Set whether to automatically create empty label files"""
    if not config.has_section("LabelFiles"):
        config.add_section("LabelFiles")
    config.set("LabelFiles", "auto_create_labels", str(enabled).lower())

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)



def get_window_size():
    """Get saved window size"""
    try:
        width = config.getint("Window", "width")
        height = config.getint("Window", "height")
        return width, height
    except:
        ERROR("width or height is not a valid integer.")
        return None, None  # Default size


def save_window_size(width, height):
    """Save window size"""
    if not config.has_section("Window"):
        config.add_section("Window")
    config.set("Window", "width", str(width))
    config.set("Window", "height", str(height))

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)



def get_window_position():
    """Get saved window position"""
    try:
        x = config.getint("Window", "x")
        y = config.getint("Window", "y")
        return x, y
    except:
        ERROR("x or y is not a valid integer.")
        return None, None  # Default position

def save_window_position(x, y):
    """Save window position"""
    if not config.has_section("Window"):
        config.add_section("Window")
    config.set("Window", "x", str(x))
    config.set("Window", "y", str(y))

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)


# UI Settings configuration functions
def get_show_class_id_buttons():
    """Get whether to show class ID buttons panel"""
    try:
        return config.getboolean("UISettings", "show_class_id_buttons")
    except:
        return False  # Default to False (current setting)

def get_show_text_box():
    """Get whether to show text box"""
    try:
        return config.getboolean("UISettings", "show_text_box")
    except:
        return True  # Default to True (current setting)

def get_show_preview():
    """Get whether to show preview panel"""
    try:
        return config.getboolean("UISettings", "show_preview")
    except:
        return True  # Default to True (current setting)

def get_show_input_box():
    """Get whether to show input box"""
    try:
        return config.getboolean("UISettings", "show_input_box")
    except:
        return True  # Default to True (current setting)

def get_show_classify_frame():
    """Get whether to show classfication buttons panel"""
    try:
        ret =  config.getboolean("UISettings", "show_classify_frame")
        return ret
    except:
        return False  # Default to False (current setting)

def get_show_cut_image():
    """Get whether to show cut image feature"""
    try:
        return config.getboolean("UISettings", "show_cut_image")
    except:
        return True  # Default to True (current setting)
    
def get_ui_label_font_size_in_config():
    """Get the font size for UI labels"""
    try:
        return config.getint("UISettings", "label_font_size")
    except:
        return 12  # Default font size

def get_show_bbox_dimensions():
    """Get whether to show bbox width/height dimensions"""
    try:
        return config.getboolean("UISettings", "show_bbox_dimensions")
    except:
        return False  # Default to False

def get_show_tilt_angle():
    """Get whether to show plate tilt angle"""
    try:
        return config.getboolean("UISettings", "show_tilt_angle")
    except:
        return False  # Default to False

def get_angle_color_assist():
    """Get whether to enable angle-based color assist for tilt guideline"""
    try:
        return config.getboolean("UISettings", "angle_color_assist")
    except:
        return True  # Default to True

def save_angle_color_assist(enabled):
    """Save angle color assist setting"""
    if not config.has_section("UISettings"):
        config.add_section("UISettings")
    config.set("UISettings", "angle_color_assist", str(enabled))

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def get_iou_color_assist():
    """Get whether to enable IoU-based color assist for bbox"""
    try:
        return config.getboolean("UISettings", "iou_color_assist")
    except:
        return True  # Default to True

def save_iou_color_assist(enabled):
    """Save IoU color assist setting"""
    if not config.has_section("UISettings"):
        config.add_section("UISettings")
    config.set("UISettings", "iou_color_assist", str(enabled))

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def get_preview_zoom_scale():
    """Get preview zoom scale factor"""
    try:
        return config.getfloat("UISettings", "preview_zoom_scale")
    except:
        return 1.0  # Default to 1x (original size)

def save_preview_zoom_scale(scale):
    """Save preview zoom scale factor"""
    if not config.has_section("UISettings"):
        config.add_section("UISettings")
    config.set("UISettings", "preview_zoom_scale", str(scale))

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def get_min_bbox_width_threshold():
    from ILT_UI import DEFAULT_MIN_PLATE_WIDTH
    """Get minimum bbox width threshold for warning"""
    try:
        return config.getint("UISettings", "min_bbox_width_threshold")
    except:
        return DEFAULT_MIN_PLATE_WIDTH  # Default 70 pixels

def get_proportional_scaling():
    """Get whether to use proportional scaling (with black borders)"""
    try:
        return config.getboolean("ImageDisplay", "proportional_scaling")
    except:
        return False  # Default to False (stretch to fill canvas)

def get_timer_default_minutes():
    """Get default timer duration in minutes"""
    try:
        return config.getint("Timer", "default_minutes")
    except:
        return 10  # Default to 10 minutes

def get_timer_enabled():
    """Get whether timer is enabled"""
    try:
        return config.getboolean("Timer", "enabled")
    except:
        return False  # Default to disabled

def set_timer_enabled(enabled):
    """Set whether timer is enabled"""
    if not config.has_section("Timer"):
        config.add_section("Timer")
    
    config.set("Timer", "enabled", str(enabled).lower())
    
    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def save_timer_settings(default_minutes=None):
    """Save timer settings to config file"""
    if not config.has_section("Timer"):
        config.add_section("Timer")
    
    if default_minutes is not None:
        config.set("Timer", "default_minutes", str(default_minutes))
    
    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def ensure_timer_config():
    """Ensure Timer settings exist in config.ini without overwriting existing values"""
    if not config.has_section("Timer"):
        config.add_section("Timer")
    
    modified = False
    
    # Only set defaults if they don't exist
    if not config.has_option("Timer", "enabled"):
        config.set("Timer", "enabled", "false")
        modified = True
    
    if not config.has_option("Timer", "default_minutes"):
        config.set("Timer", "default_minutes", "10")
        modified = True
    
    # Only write to file if we made changes
    if modified:
        with open(DEFAULT_CONFI_PATH, "w") as f:
            config.write(f)

def save_ui_settings(show_class_id_buttons=None, show_text_box=None,
                    show_preview=None, show_input_box=None, show_classify_frame=None,
                    show_cut_image=None, label_font_size=10, show_bbox_dimensions=None,
                    min_bbox_width_threshold=None, proportional_scaling=None, show_tilt_angle=None):
    """Save UI settings to config file"""
    if not config.has_section("UISettings"):
        config.add_section("UISettings")

    if show_class_id_buttons is not None:
        config.set("UISettings", "show_class_id_buttons", str(show_class_id_buttons).lower())
    if show_text_box is not None:
        config.set("UISettings", "show_text_box", str(show_text_box).lower())
    if show_preview is not None:
        config.set("UISettings", "show_preview", str(show_preview).lower())
    if show_input_box is not None:
        config.set("UISettings", "show_input_box", str(show_input_box).lower())
    if label_font_size is not None:
        config.set("UISettings", "label_font_size", str(label_font_size))
    if show_classify_frame is not None:
        config.set("UISettings", "show_classify_frame", str(show_classify_frame).lower())
    if show_cut_image is not None:
        config.set("UISettings", "show_cut_image", str(show_cut_image).lower())
    if show_bbox_dimensions is not None:
        config.set("UISettings", "show_bbox_dimensions", str(show_bbox_dimensions).lower())
    if min_bbox_width_threshold is not None:
        config.set("UISettings", "min_bbox_width_threshold", str(min_bbox_width_threshold))
    if show_tilt_angle is not None:
        config.set("UISettings", "show_tilt_angle", str(show_tilt_angle).lower())

    # Save proportional_scaling to ImageDisplay section
    if proportional_scaling is not None:
        if not config.has_section("ImageDisplay"):
            config.add_section("ImageDisplay")
        config.set("ImageDisplay", "proportional_scaling", str(proportional_scaling).lower())

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def get_all_ui_settings():
    """Get all UI settings as a dictionary"""
    return {
        'show_class_id_buttons': get_show_class_id_buttons(),
        'show_text_box': get_show_text_box(),
        'show_preview': get_show_preview(),
        'show_input_box': get_show_input_box(),
        'show_classify_frame': get_show_classify_frame(),
        'show_cut_image': get_show_cut_image(),
        'label_font_size': get_ui_label_font_size_in_config(),
        'show_bbox_dimensions': get_show_bbox_dimensions(),
        'min_bbox_width_threshold': get_min_bbox_width_threshold(),
        'proportional_scaling': get_proportional_scaling(),
        'timer_enabled': get_timer_enabled(),
        'timer_default_minutes': get_timer_default_minutes(),
        'show_tilt_angle': get_show_tilt_angle()
    }

def get_recent_plates():
    """Get recent plates from config"""
    try:
        plates_str = config.get("PlateMemory", "recent_plates")
        if plates_str.strip():
            return [plate.strip() for plate in plates_str.split(",") if plate.strip()]
        return []
    except:
        return []

def save_recent_plates(plates_list):
    """Save recent plates to config"""
    try:
        if not config.has_section("PlateMemory"):
            config.add_section("PlateMemory")

        # Convert list to comma-separated string
        plates_str = ",".join(plates_list)
        config.set("PlateMemory", "recent_plates", plates_str)

        with open(DEFAULT_CONFI_PATH, "w") as f:
            config.write(f)
        return True
    except Exception as e:
        ERROR("Failed to save recent plates: {}", e)
        return False


# Hotkey configuration functions
DEFAULT_HOTKEYS = {
    'previous_image': '<Left>',
    'next_image': '<Right>',
    'toggle_drawing_mode': '<Control_L>',
    'delete_bbox': '<Delete>',
    'search_file': '<Control-f>',
    'quick_correct': '<t>',
    'cut_image': '<Shift-C>',
    'delete_image': '',  # Default unset - user can configure
}

# Friendly names for hotkey actions
HOTKEY_ACTION_NAMES = {
    'previous_image': 'Previous Image',
    'next_image': 'Next Image',
    'toggle_drawing_mode': 'Toggle Drawing Mode',
    'delete_bbox': 'Delete Bbox',
    'search_file': 'Search File',
    'quick_correct': 'Quick Correct',
    'cut_image': 'Cut Image',
    'delete_image': 'Delete Image',
}

def get_default_hotkeys():
    """Get default hotkey mappings"""
    return DEFAULT_HOTKEYS.copy()

def get_hotkey(action_name):
    """Get hotkey for specific action"""
    try:
        hotkey = config.get("Hotkeys", action_name)
        return hotkey
    except:
        # Return default if not found
        return DEFAULT_HOTKEYS.get(action_name, '')

def get_all_hotkeys():
    """Get all hotkey mappings"""
    hotkeys = {}
    for action in DEFAULT_HOTKEYS.keys():
        hotkeys[action] = get_hotkey(action)
    return hotkeys

def save_hotkeys(hotkey_dict):
    """Save hotkey mappings to config file"""
    if not config.has_section("Hotkeys"):
        config.add_section("Hotkeys")

    for action, hotkey in hotkey_dict.items():
        config.set("Hotkeys", action, hotkey)

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def reset_hotkeys_to_default():
    """Reset all hotkeys to default values"""
    save_hotkeys(DEFAULT_HOTKEYS)

def get_hotkey_action_name(action_key):
    """Get friendly name for hotkey action"""
    return HOTKEY_ACTION_NAMES.get(action_key, action_key)

