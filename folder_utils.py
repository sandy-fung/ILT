import os
from log_levels import DEBUG, INFO, ERROR
import shutil


def scan_image_folder(img_folder):
    images = [
        f for f in os.listdir(img_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    images_path = [
        os.path.join(img_folder, f)
        for f in images
    ]
    return images, images_path

def scan_label_folder(images, label_folder):
    labels = []
    labels_path = []

    for f in images:
        label = os.path.splitext(f)[0] + ".txt"
        label_path = os.path.join(label_folder, label)

        labels.append(label)
        labels_path.append(label_path)
    return labels, labels_path

def load_label(path):
    """Load label file, return empty string if not exists"""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        DEBUG("Label loaded from path: {}", path)
        return content
    else:
        DEBUG("Label file not found: {}, returning empty content", path)
        return ""

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        INFO("Moved file from {} to {}", src, dst)
    except OSError as e:
        ERROR("Error moving file from {} to {}: {}", src, dst, e)
        raise e