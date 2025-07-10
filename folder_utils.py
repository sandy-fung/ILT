import os
import config_utils
from log_levels import DEBUG, INFO, ERROR

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

def ensure_labels_exist(labels_path):
    for f in labels_path:
        if not os.path.exists(f):
            open(f, 'w').close()  # Create empty txt

def load_label(path):
    with open(path, 'r', encoding = 'utf-8') as f:
        content = f.read()
    DEBUG("Label loaded from path: {}", path)
    return content