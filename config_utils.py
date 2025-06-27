from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

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
    
    with open("config.ini", "w") as f:
        config.write(f)

def get_image_index():
    try:
        return config.getint("Path", "image_index")
    except:
        return 0

def save_image_index(index):
    if not config.has_section("Path"):
        config.add_section("Path")
    config.set("Path", "image_index", index)
    with open("config.ini", "w") as f:
        config.write(f)


def save_image_info(width, height):
    if not config.has_section("ImageInfo"):
        config.add_section("ImageInfo")
    config.set("ImageInfo", "image_width", str(width))
    config.set("ImageInfo", "image_height", str(height))
    with open("config.ini", "w") as f:
        config.write(f)