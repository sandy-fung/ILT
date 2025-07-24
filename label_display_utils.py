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

    def move_by_canvas_delta(self, dx, dy, canvas_width, canvas_height):
        """
        用 canvas 像素增量移動 bounding box
        
        Args:
            dx (float): X 方向像素增量
            dy (float): Y 方向像素增量
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
        """
        # 轉換像素增量為 YOLO 比例增量
        dx_ratio = dx / canvas_width
        dy_ratio = dy / canvas_height
        
        # 更新中心點座標
        self.cx_ratio += dx_ratio
        self.cy_ratio += dy_ratio
        
        # 應用邊界約束 (確保 bounding box 不超出影像邊界)
        self.apply_boundary_constraints(canvas_width, canvas_height)

    def apply_boundary_constraints(self, canvas_width, canvas_height):
        """
        確保 bounding box 不超出影像邊界
        
        Args:
            canvas_width (int): Canvas 寬度  
            canvas_height (int): Canvas 高度
        """
        # 計算 bounding box 的邊界
        half_w = max(0.001, min(0.5, self.w_ratio / 2))  # Constrain to valid range
        half_h = max(0.001, min(0.5, self.h_ratio / 2))
        
        # 約束中心點，確保 bounding box 完全在 [0,1] 範圍內
        min_cx = half_w
        max_cx = 1.0 - half_w
        min_cy = half_h  
        max_cy = 1.0 - half_h
        
        # 應用約束 (加強邊界檢查)
        if min_cx < max_cx and min_cy < max_cy:  # 確保約束有效
            self.cx_ratio = max(min_cx, min(max_cx, self.cx_ratio))
            self.cy_ratio = max(min_cy, min(max_cy, self.cy_ratio))
        else:
            # Handle edge case: oversized bounding box
            self.cx_ratio = 0.5
            self.cy_ratio = 0.5
            DEBUG("Applied fallback constraints for oversized box")

    def get_canvas_center(self, canvas_width, canvas_height):
        """
        取得 canvas 中心點座標
        
        Args:
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
            
        Returns:
            tuple: (cx_pixels, cy_pixels) Canvas 像素座標
        """
        cx_pixels = self.cx_ratio * canvas_width
        cy_pixels = self.cy_ratio * canvas_height
        return cx_pixels, cy_pixels

    def set_canvas_position(self, cx, cy, canvas_width, canvas_height):
        """
        設定 canvas 位置
        
        Args:
            cx (float): 中心 X 座標 (canvas 像素)
            cy (float): 中心 Y 座標 (canvas 像素)
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
        """
        self.cx_ratio = cx / canvas_width
        self.cy_ratio = cy / canvas_height
        
        # 應用邊界約束
        self.apply_boundary_constraints(canvas_width, canvas_height)

    def is_on_resize_handle(self, x, y, canvas_width, canvas_height, handle_size=10):
        """
        檢測點擊是否在 resize handle 上 (只有右下角)
        
        Args:
            x (float): 點擊的 X 座標 (canvas 像素)
            y (float): 點擊的 Y 座標 (canvas 像素)
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
            handle_size (int): Handle 尺寸 (default: 10 pixels)
            
        Returns:
            bool: 如果在 resize handle 上返回 True，否則返回 False
        """
        # 轉換為 canvas 座標的邊界框
        x1, y1, x2, y2 = convert_label_to_canvas_coords(self, canvas_width, canvas_height)
        
        # 只檢查右下角 handle
        return (x2 - handle_size <= x <= x2 and y2 - handle_size <= y <= y2)

    def resize(self, new_width_pixels, new_height_pixels, canvas_width, canvas_height):
        """
        調整 bounding box 大小，保持中心點不變
        
        Args:
            new_width_pixels (float): 新的寬度 (canvas 像素)
            new_height_pixels (float): 新的高度 (canvas 像素) 
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
        """
        # 設定最小尺寸限制
        min_width_pixels = max(10, new_width_pixels)
        min_height_pixels = max(10, new_height_pixels)
        
        # 轉換為 YOLO 比例
        new_w_ratio = min_width_pixels / canvas_width
        new_h_ratio = min_height_pixels / canvas_height
        
        # 更新尺寸
        self.w_ratio = new_w_ratio
        self.h_ratio = new_h_ratio
        
        # 應用邊界約束 (確保調整後的 box 不超出邊界)
        self.apply_boundary_constraints(canvas_width, canvas_height)
        
        DEBUG("Resized label: new size=({:.3f}, {:.3f}), canvas_size=({}, {})", 
              self.w_ratio, self.h_ratio, canvas_width, canvas_height)

    def resize_by_delta(self, dx, dy, canvas_width, canvas_height):
        """
        根據滑鼠拖拽增量調整大小
        保持中心點不變，只調整寬度和高度
        
        Args:
            dx (float): X 方向增量 (canvas 像素)
            dy (float): Y 方向增量 (canvas 像素)
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
        """
        # 獲取當前像素尺寸
        _, _, current_width, current_height = label_to_pixel_position(self, canvas_width, canvas_height)
        
        # 根據增量計算新的寬度和高度
        # Calculate new dimensions based on delta
        new_width = current_width + dx
        new_height = current_height + dy
        
        # 應用新的尺寸（resize 方法會保持中心點不變）
        self.resize(new_width, new_height, canvas_width, canvas_height)


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


def delta_canvas_to_yolo(dx, dy, canvas_width, canvas_height):
    """
    轉換 canvas 像素增量為 YOLO 比例增量
    
    Args:
        dx (float): X 方向像素增量
        dy (float): Y 方向像素增量 
        canvas_width (int): Canvas 寬度
        canvas_height (int): Canvas 高度
        
    Returns:
        tuple: (dx_ratio, dy_ratio) YOLO 比例增量
    """
    dx_ratio = dx / canvas_width
    dy_ratio = dy / canvas_height
    return dx_ratio, dy_ratio


def validate_yolo_bounds(cx_ratio, cy_ratio, w_ratio, h_ratio):
    """
    驗證 YOLO 座標是否在合法範圍 [0,1]
    
    Args:
        cx_ratio (float): 中心 X 比例
        cy_ratio (float): 中心 Y 比例
        w_ratio (float): 寬度比例
        h_ratio (float): 高度比例
        
    Returns:
        bool: 是否在合法範圍內
    """
    # 檢查所有值是否在 [0,1] 範圍內
    if not (0 <= cx_ratio <= 1 and 0 <= cy_ratio <= 1):
        return False
    if not (0 <= w_ratio <= 1 and 0 <= h_ratio <= 1):
        return False
        
    # 檢查 bounding box 是否完全在影像範圍內
    half_w = w_ratio / 2
    half_h = h_ratio / 2
    
    if cx_ratio - half_w < 0 or cx_ratio + half_w > 1:
        return False
    if cy_ratio - half_h < 0 or cy_ratio + half_h > 1:
        return False
        
    return True


def calculate_vertical_overlap(label1, label2):
    """
    計算兩個標籤的垂直重疊率
    
    Args:
        label1 (LabelObject): 第一個標籤
        label2 (LabelObject): 第二個標籤
        
    Returns:
        float: 垂直重疊率 (0-1)
    """
    # 獲取兩個標籤的垂直範圍
    y1_top = label1.cy_ratio - label1.h_ratio / 2
    y1_bottom = label1.cy_ratio + label1.h_ratio / 2
    y2_top = label2.cy_ratio - label2.h_ratio / 2
    y2_bottom = label2.cy_ratio + label2.h_ratio / 2
    
    # 計算重疊區域
    overlap_top = max(y1_top, y2_top)
    overlap_bottom = min(y1_bottom, y2_bottom)
    
    if overlap_top >= overlap_bottom:
        return 0.0  # 無重疊
    
    # 計算重疊率（相對於較小的高度）
    overlap_height = overlap_bottom - overlap_top
    min_height = min(label1.h_ratio, label2.h_ratio)
    
    return overlap_height / min_height if min_height > 0 else 0.0


def is_same_plate(label, group, overlap_threshold=0.5):
    """
    判斷標籤是否屬於同一車牌
    
    Args:
        label (LabelObject): 要檢查的標籤
        group (list): 車牌分組中的標籤列表
        overlap_threshold (float): 垂直重疊率閾值
        
    Returns:
        bool: 是否屬於同一車牌
    """
    if not group:
        return False
    
    # 檢查與組內任一標籤的垂直重疊率
    for group_label in group:
        if calculate_vertical_overlap(label, group_label) >= overlap_threshold:
            return True
    
    return False


def group_labels_by_plate(labels):
    """
    將標籤按車牌分組
    
    Args:
        labels (list): LabelObject 列表
        
    Returns:
        list: 分組後的標籤列表，每個元素是一個車牌的標籤列表
    """
    if not labels:
        return []
    
    # 先按 Y 座標排序，方便分組
    sorted_labels = sorted(labels, key=lambda l: l.cy_ratio)
    
    groups = []
    for label in sorted_labels:
        assigned = False
        for group in groups:
            if is_same_plate(label, group):
                group.append(label)
                assigned = True
                break
        
        if not assigned:
            groups.append([label])
    
    DEBUG("Grouped {} labels into {} plates", len(labels), len(groups))
    return groups


def sort_labels_by_position(labels):
    """
    對標籤進行分組並排序
    
    Args:
        labels (list): LabelObject 列表
        
    Returns:
        tuple: (排序後的 LabelObject 列表, 車牌數量)
    """
    if not labels:
        return [], 0
    
    # 分組
    groups = group_labels_by_plate(labels)
    
    # 對每組內的標籤按 X 座標排序
    sorted_labels = []
    for group_idx, group in enumerate(groups):
        sorted_group = sorted(group, key=lambda l: l.cx_ratio)
        sorted_labels.extend(sorted_group)
        DEBUG("Plate {}: {} labels sorted by X position", group_idx + 1, len(sorted_group))
    
    INFO("Sorted {} labels in {} plates", len(sorted_labels), len(groups))
    return sorted_labels, len(groups)

def parse_label_text(text: str):
    labels = []
    lines = text.strip().splitlines()
    for line in lines:
        parts = line.strip().split()
        if not line:
            continue
        if len(parts) == 5:
            try:
                class_id = int(parts[0])
                cx = float(parts[1])
                cy = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])
                labels.append(LabelObject(class_id, cx, cy, w, h))
            except ValueError:
                ERROR("Invalid label format in line: {}", line)
    return labels