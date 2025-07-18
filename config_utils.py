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