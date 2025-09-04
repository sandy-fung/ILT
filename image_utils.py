import config_utils
import cv2
from PIL import Image, ImageTk
from log_levels import DEBUG, INFO, ERROR
import folder_utils



def load_image(path):
    image = cv2.imread(path)
    actual_path = path  # 記錄實際載入的路徑
    
    # 如果原路徑載入失敗，嘗試往上一層目錄搜尋
    if image is None:
        DEBUG("Failed to load image from original path: {}, trying parent directory", path)
        parent_path = folder_utils.find_image_in_parent_directory(path)
        if parent_path:
            image = cv2.imread(parent_path)
            if image is not None:
                actual_path = parent_path
                DEBUG("Successfully loaded image from parent directory: {}", parent_path)
    
    # 如果仍然載入失敗
    if image is None:
        ERROR("Failed to load image from path: {} (also checked parent directory)", path)
        return
    
    DEBUG("Image loaded from path: {}", actual_path)

    image_height, image_width = image.shape[:2]
    DEBUG("Image loaded with height: {}, width: {}", image_height, image_width)

    config_utils.save_image_info(image_height, image_width)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image_pil = Image.fromarray(image_rgb)
    return image_pil

def resize_image(image_pil, size):
    rsz_image = image_pil.resize(size, Image.Resampling.LANCZOS)
    DEBUG("Image resized to: {}", size)
    return rsz_image

def convert_to_tk(rsz_image):
    tk_image = ImageTk.PhotoImage(rsz_image)
    return tk_image