from PIL import Image
import os
import shutil
from pathlib import Path


def sort_labels(labels):
    """Sort YOLO labels by center x position (cx)"""
    return sorted(labels, key=lambda x: x[1])  # x[1] is cx


def canvas_x_to_image_x(canvas_x, canvas_width, image_width):
    """Convert x from canvas to image-relative x"""
    return int(canvas_x * image_width / canvas_width)

def left_case(new_labels, abs_cx, abs_w, cut_x, cls, cy, h):
    new_cx = abs_cx
    new_w = abs_w
    new_image_width = cut_x 
    new_labels.append([
                    cls,
                    new_cx / new_image_width,
                    cy,  # cy and h are unaffected
                    new_w / new_image_width,
                    h
                ])

def right_case(new_labels, abs_cx, abs_w, cut_x, cls, cy, h, image_width):
    new_cx = abs_cx - cut_x
    new_w = abs_w
    new_image_width =  image_width - cut_x
    new_labels.append([
                    cls,
                    new_cx / new_image_width,
                    cy,  # cy and h are unaffected
                    new_w / new_image_width,
                    h
                ])
    
    
def adjust_labels_after_split(labels, cut_x, image_width, keep_left=True):
    """Adjust label positions for left or right part after image split"""
    new_labels = []
 
    
    
    for label in labels:
        cls, cx, cy, w, h = label
        abs_cx = cx * image_width
        abs_w = w * image_width
        
        # Full object bounding box in pixels
        x0 = abs_cx - abs_w / 2
        x1 = abs_cx + abs_w / 2

        # Decide if it belongs to the left or right side
        if keep_left and x1 <= cut_x:
            # Entirely on the left side
            if keep_left is False:
                continue
            left_case(new_labels, abs_cx, abs_w, cut_x, cls, cy, h)
            
        elif not keep_left and x0 >= cut_x:
            # Entirely on the right side  
            if keep_left is True:
                continue
            right_case(new_labels, abs_cx, abs_w, cut_x, cls, cy, h, image_width)
            
        else:
            # Object crosses the border → juge by cut_x and abs_cx
            if abs_cx <= cut_x:
                # Object is on the left side 
                if keep_left is False:
                    continue
                left_case(new_labels, abs_cx, abs_w, cut_x, cls, cy, h)
                
            else:
                # on the right side
                if keep_left is True:
                    continue
                right_case(new_labels, abs_cx, abs_w, cut_x, cls, cy, h, image_width)
   

    return new_labels

def parse_labels(label_path):
    labels = []
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            labels.append([int(parts[0])] + [float(x) for x in parts[1:]])
    return labels

def get_ocr_string(labels):
    from Words_Label_mapping import get_label
    class_ids = []
    for label in labels:
        cls, cx, cy, w, h = label
        
        class_ids.append(get_label(cls))
    return "".join(map(str, class_ids))
            
def __split_image_and_labels(image_path, label_path, labels, cut_x, output_dir):
    """
    Split image and YOLO labels based on x position.

    Parameters
    ----------
    image_path : str
    label_path : str
    labels : list[list[class_id, cx, cy, w, h]]
    cut_x : int
        Image-based X coordinate to split at.
    output_dir : str
        Directory to save cropped images and labels.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory created: {output_dir}")
    # Load image
    image = Image.open(image_path)
    image_width, image_height = image.size

    # Get the base names of image_path and label_path
    image_base_name = os.path.splitext(os.path.basename(image_path))[0]
    label_base_name = os.path.splitext(os.path.basename(label_path))[0]


    # ==== Crop left =====
    left_image = image.crop((0, 0, cut_x, image_height))
    left_labels = adjust_labels_after_split(labels, cut_x, image_width, keep_left=True)
    ocr_str = get_ocr_string(left_labels)
    
    # Append "left" to the base names
    left_image_path = os.path.join(output_dir, f"{ocr_str}_{image_base_name}_left.jpg")
    left_label_path = os.path.join(output_dir, f"{ocr_str}_{label_base_name}_left.txt")
    
    left_image.save(left_image_path)
    save_yolo_labels(left_labels, left_label_path)


    # ==== Crop right =====
    right_image = image.crop((cut_x, 0, image_width, image_height))
    right_labels = adjust_labels_after_split(labels, cut_x, image_width, keep_left=False)
    ocr_str = get_ocr_string(right_labels)
    
    # Append "right" to the base names (if needed)
    right_image_path = os.path.join(output_dir, f"{ocr_str}_{image_base_name}_right.jpg")
    right_label_path = os.path.join(output_dir, f"{ocr_str}_{label_base_name}_right.txt")
    
    right_image.save(right_image_path)
    save_yolo_labels(right_labels, right_label_path)

def split_image_and_labels(image_path, label_path, cut_x,canvas_width, output_dir):
    # Load labels
    labels = parse_labels(label_path)
    
    # Optional: sort
    labels = sort_labels(labels)
    
    # Convert canvas_x to image-relative x
    image = Image.open(image_path)
    image_width = image.size[0]
    cut_x_in_image = canvas_x_to_image_x(cut_x, canvas_width, image_width)
    __split_image_and_labels(image_path, label_path, labels, cut_x_in_image, output_dir)

def save_yolo_labels(labels, out_path):
    """Save YOLO labels to .txt file"""
    with open(out_path, "w") as f:
        for lbl in labels:
            cls, cx, cy, w, h = lbl
            f.write(f"{int(cls)} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
            # print(f"Saved label: {int(cls)} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
            
            
if __name__ == "__main__":
    
    image_path = Path(r"E:\car_plate_images\tmp\woody_s_cam_June/SpecialPlates_1365429320622837_000177_frame10650_0.jpg")
    label_path = Path(r"E:\car_plate_images\tmp\woody_s_cam_June/SpecialPlates_1365429320622837_000177_frame10650_0.txt")
    canvas_width = 800
    canvas_click_x = 420  # e.g., mouse click
    
    # Load labels
    labels = parse_labels(label_path)
    
    # Optional: sort
    labels = sort_labels(labels)
    
    # Convert canvas_x to image-relative x
    image = Image.open(image_path)
    image_width = image.size[0]
    cut_x = canvas_x_to_image_x(canvas_click_x, canvas_width, image_width)
    
    # Split and export
    split_image_and_labels(image_path, label_path, labels, cut_x, "output_split")
