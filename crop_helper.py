import folder_utils
import image_utils
import label_display_utils
import os
import cv2
from pathlib import Path
from label_display_utils import LabelObject
from log_levels import DEBUG, INFO, ERROR

OUTPUT_DIR = "crop"



def start_cropping(image_folder_path, images_path, labels_path):
        output_dir = os.path.join(image_folder_path, "crop")
        print(output_dir)  # Output: /path/to/images/crop
        if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
        for index, image_path in enumerate(images_path):
            # print(f"images: {images_path[index]}")
            # labels_path[self.image_index]
            current_label_path = labels_path[index]
            # print(f"labels: {labels_path[index]}")
            # current_labels = label_display_utils.parse_label_file(current_label_path)
            # print(f"current_labels: {current_labels}")
            text = folder_utils.load_label(current_label_path)
            labels = label_display_utils.parse_label_text(text)  
         
            crop_and_save_labels(image_path, labels, current_label_path, output_dir)
            
def crop_and_save_labels(image_path, labels, current_label_path, output_dir):
    """
    Crop objects from an image based on YOLO labels and save them.

    Args:
        image_path (str): Path to the input image.
        labels (list): List of YOLO labels, where each label is a tuple (class_id, x_center, y_center, width, height).
        current_label_path (str): Base name for the cropped images.
        output_dir (str): Directory to save the cropped images.

    Returns:
        None
    """
    # Open the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to open image: {image_path}")
        return

    # Get image dimensions
    img_height, img_width, _ = image.shape

    # Process each label
    for label_index,label in enumerate(labels):
    # for label_index, (class_id, cx_ratio, cy_ratio, w_ratio, h_ratio) in enumerate(labels):
        # Convert YOLO format to pixel coordinates
        class_id, cx, cy, w, h = label.class_id, label.cx_ratio, label.cy_ratio, label.w_ratio, label.h_ratio
        x_min = int((cx - w / 2) * img_width)
        y_min = int((cy - h / 2) * img_height)
        x_max = int((cx + w / 2) * img_width)
        y_max = int((cy + h / 2) * img_height)

        # Crop the image
        cropped_image = image[y_min:y_max, x_min:x_max]

        # Construct the output file name
        output_file_name = f"{Path(current_label_path).stem}_{label_index}.jpg"
        output_file_path = os.path.join(output_dir, output_file_name)

        # Save the cropped image
        cv2.imwrite(output_file_path, cropped_image)
        DEBUG(f"Saved cropped image: {output_file_path}")