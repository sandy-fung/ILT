import config_utils
import cv2
from PIL import Image, ImageTk
from log_levels import DEBUG, INFO, ERROR



def load_image(path):
    image = cv2.imread(path)
    if image is None:
        ERROR("Failed to load image from path: {}", path)
        return
    DEBUG("Image loaded from path: {}", path)

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