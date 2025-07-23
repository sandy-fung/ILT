from configparser import ConfigParser

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

def save_ui_settings(show_class_id_buttons=None, show_text_box=None, 
                    show_preview=None, show_input_box=None):
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

    with open(DEFAULT_CONFI_PATH, "w") as f:
        config.write(f)

def get_all_ui_settings():
    """Get all UI settings as a dictionary"""
    return {
        'show_class_id_buttons': get_show_class_id_buttons(),
        'show_text_box': get_show_text_box(),
        'show_preview': get_show_preview(),
        'show_input_box': get_show_input_box()
    }