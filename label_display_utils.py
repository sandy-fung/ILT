from log_levels import DEBUG, INFO, ERROR
import os


class LabelObject:
    def __init__(self, class_id: int, cx_ratio: float, cy_ratio: float, w_ratio: float, h_ratio: float):
        self.class_id = class_id
        self.cx_ratio = cx_ratio
        self.cy_ratio = cy_ratio
        self.w_ratio = w_ratio
        self.h_ratio = h_ratio
        self.selected = False  # 選中狀態標記

    def update(self, cx: float, cy: float, width: float, height: float, canvas_size):
        canv_x, canv_y = canvas_size
        self.cx_ratio = cx / canv_x
        self.cy_ratio = cy / canv_y
        self.w_ratio = width / canv_x
        self.h_ratio = height / canv_y

    def to_yolo(self):
        ret = f"{self.class_id} {self.cx_ratio:.17f} {self.cy_ratio:.17f} {self.w_ratio:.17f} {self.h_ratio:.17f}"
        DEBUG("Converted to YOLO format: {}", ret)
        return ret

    def contains(self, x, y, canvas_width, canvas_height):
        """
        判斷點擊位置是否在此 bounding box 內
        
        Args:
            x (float): 點擊的 x 座標 (canvas 像素)
            y (float): 點擊的 y 座標 (canvas 像素)
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
            
        Returns:
            bool: 如果點擊在框內則返回 True
        """
        # 轉換為 canvas 座標的邊界框
        x1, y1, x2, y2 = convert_label_to_canvas_coords(self, canvas_width, canvas_height)
        
        # 檢查點擊是否在矩形內
        return x1 <= x <= x2 and y1 <= y <= y2

    def set_selected(self, selected):
        """
        設定選中狀態
        
        Args:
            selected (bool): 是否選中
        """
        self.selected = selected


def label_to_pixel_position(label, canvas_width, canvas_height):
    """Convert a label object to bounding box coordinates in pixel format"""
    
    # Convert normalized YOLO format to pixel coordinates
    box_width = label.w_ratio * canvas_width
    box_height = label.h_ratio * canvas_height
    center_x = label.cx_ratio * canvas_width
    center_y = label.cy_ratio * canvas_height
    
    DEBUG("Canvas size: {}, {}", canvas_width, canvas_height)
    DEBUG("Converting label to pixel position: cx={}, cy={}, w={}, h={}", 
          center_x, center_y, box_width, box_height)
    
    return center_x, center_y, box_width, box_height


def canvas_rectangle_to_center_size(x1, y1, x2, y2):
    """Convert rectangle coordinates to center position and size"""
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y, width, height


def calculate_yolo_format(x1, y1, x2, y2, img_w, img_h):
    """
    Calculate YOLO format values (center x, center y, width ratio, height ratio).

    Args:
        x1 (int): Starting x-coordinate.
        y1 (int): Starting y-coordinate.
        x2 (int): Ending x-coordinate.
        y2 (int): Ending y-coordinate.
        img_w (int): Image width.
        img_h (int): Image height.

    Returns:
        tuple: (cx, cy, w_ratio, h_ratio)
    """
    cx = (x1 + x2) / 2 / img_w
    cy = (y1 + y2) / 2 / img_h
    w_ratio = abs(x2 - x1) / img_w
    h_ratio = abs(y2 - y1) / img_h
    return cx, cy, w_ratio, h_ratio


def parse_label_file(file_path):
    """
    Parse a YOLO format label file and return a list of LabelObject instances.
    
    Args:
        file_path (str): Path to the label file
        
    Returns:
        list: List of LabelObject instances
    """
    labels = []
    
    if not os.path.exists(file_path):
        DEBUG("Label file does not exist: {}", file_path)
        return labels
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                parts = line.split()
                if len(parts) == 5:
                    try:
                        class_id = int(parts[0])
                        cx_ratio = float(parts[1])
                        cy_ratio = float(parts[2])
                        w_ratio = float(parts[3])
                        h_ratio = float(parts[4])
                        
                        label = LabelObject(class_id, cx_ratio, cy_ratio, w_ratio, h_ratio)
                        labels.append(label)
                        DEBUG("Loaded label: {} {:.6f} {:.6f} {:.6f} {:.6f}", 
                              class_id, cx_ratio, cy_ratio, w_ratio, h_ratio)
                              
                    except ValueError as e:
                        ERROR("Error parsing line {} in {}: {}", line_num, file_path, e)
                else:
                    ERROR("Invalid format in line {} of {}: expected 5 values, got {}", 
                          line_num, file_path, len(parts))
                          
    except Exception as e:
        ERROR("Error reading label file {}: {}", file_path, e)
    
    INFO("Loaded {} labels from {}", len(labels), file_path)
    return labels


def convert_label_to_canvas_coords(label, canvas_width, canvas_height):
    """
    Convert a label to canvas drawing coordinates (top-left and bottom-right).
    
    Args:
        label (LabelObject): The label object
        canvas_width (int): Canvas width in pixels
        canvas_height (int): Canvas height in pixels
        
    Returns:
        tuple: (x1, y1, x2, y2) coordinates for canvas drawing
    """
    center_x, center_y, box_width, box_height = label_to_pixel_position(
        label, canvas_width, canvas_height
    )
    
    # Convert center+size to top-left and bottom-right coordinates
    x1 = center_x - box_width / 2
    y1 = center_y - box_height / 2
    x2 = center_x + box_width / 2
    y2 = center_y + box_height / 2
    
    return x1, y1, x2, y2