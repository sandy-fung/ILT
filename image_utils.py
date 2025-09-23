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

def resize_image_aspect_ratio(image_pil, canvas_size):
    """
    Resize image maintaining aspect ratio and add black borders

    Args:
        image_pil: PIL Image object
        canvas_size: tuple (width, height) of target canvas

    Returns:
        tuple: (resized_image, actual_image_rect)
            - resized_image: PIL Image with black borders
            - actual_image_rect: dict with keys 'x', 'y', 'width', 'height'
                                representing actual image area in canvas
    """
    canvas_width, canvas_height = canvas_size
    img_width, img_height = image_pil.size

    # Calculate scale to fit image in canvas while maintaining aspect ratio
    scale_x = canvas_width / img_width
    scale_y = canvas_height / img_height
    scale = min(scale_x, scale_y)

    # Calculate new dimensions (ensure minimum size of 1)
    new_width = max(1, int(img_width * scale))
    new_height = max(1, int(img_height * scale))

    # Resize image
    resized = image_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create black canvas
    result = Image.new('RGB', (canvas_width, canvas_height), color='black')

    # Calculate position to center the image
    x_offset = (canvas_width - new_width) // 2
    y_offset = (canvas_height - new_height) // 2

    # Paste resized image onto black canvas
    result.paste(resized, (x_offset, y_offset))

    # Return image and actual image area information
    actual_rect = {
        'x': x_offset,
        'y': y_offset,
        'width': new_width,
        'height': new_height
    }

    DEBUG("Image resized with aspect ratio: original {}x{}, new {}x{}, offset ({}, {})",
          img_width, img_height, new_width, new_height, x_offset, y_offset)

    return result, actual_rect

def convert_to_tk(rsz_image):
    tk_image = ImageTk.PhotoImage(rsz_image)
    return tk_image