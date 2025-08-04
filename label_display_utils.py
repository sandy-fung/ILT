from log_levels import DEBUG, INFO, ERROR
import os
MAX_OVERLAP = 0.6
# MAX_DIST_WIDTH_RATIO = 1.15
# MIN_DIST_WIDTH_RATIO = 0.7
# MAX_DISTANCE_VARIANCE = 0.01

class LabelObject:
    def __init__(self, class_id: int, cx_ratio: float, cy_ratio: float, w_ratio: float, h_ratio: float, line_index = None):
        self.class_id = class_id
        self.cx_ratio = cx_ratio
        self.cy_ratio = cy_ratio
        self.w_ratio = w_ratio
        self.h_ratio = h_ratio
        self.selected = False  # 選中狀態標記
        self.line_index = line_index

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
        # 首先約束尺寸，防止bbox大於畫面
        self.w_ratio = max(0.001, min(1.0, self.w_ratio))  # 寬度限制在 [0.001, 1.0]
        self.h_ratio = max(0.001, min(1.0, self.h_ratio))  # 高度限制在 [0.001, 1.0]
        
        # 計算 bounding box 的半寬和半高
        half_w = self.w_ratio / 2
        half_h = self.h_ratio / 2
        
        # 計算中心點的允許範圍，確保 bounding box 完全在 [0,1] 範圍內
        min_cx = half_w
        max_cx = 1.0 - half_w
        min_cy = half_h  
        max_cy = 1.0 - half_h
        
        # 約束中心點位置
        if min_cx <= max_cx and min_cy <= max_cy:  # 確保約束範圍有效
            self.cx_ratio = max(min_cx, min(max_cx, self.cx_ratio))
            self.cy_ratio = max(min_cy, min(max_cy, self.cy_ratio))
        else:
            # 極端情況：bbox尺寸過大，強制調整
            self.w_ratio = min(1.0, self.w_ratio)
            self.h_ratio = min(1.0, self.h_ratio)
            self.cx_ratio = 0.5
            self.cy_ratio = 0.5
            DEBUG("Applied emergency constraints for oversized box: w={:.3f}, h={:.3f}", 
                  self.w_ratio, self.h_ratio)

    def apply_resize_boundary_constraints(self, canvas_width, canvas_height, handle_type):
        """
        Resize專用邊界約束：只約束被拖曳的邊，固定相對邊不動
        
        Args:
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度  
            handle_type (str): 正在拖曳的handle類型
        """
        # 先約束尺寸在合理範圍
        self.w_ratio = max(0.001, min(1.0, self.w_ratio))  
        self.h_ratio = max(0.001, min(1.0, self.h_ratio))
        
        # 計算當前邊界位置（像素座標）
        half_w = self.w_ratio / 2
        half_h = self.h_ratio / 2
        
        left_edge = self.cx_ratio - half_w
        right_edge = self.cx_ratio + half_w
        top_edge = self.cy_ratio - half_h
        bottom_edge = self.cy_ratio + half_h
        
        # 根據拖曳的handle類型，只約束對應的邊，固定相對邊
        adjusted = False
        
        if handle_type in ['left', 'top-left', 'bottom-left']:
            # 拖曳左邊：如果左邊越界，固定右邊位置，調整左邊到邊界
            if left_edge < 0:
                fixed_right = right_edge  # 固定right邊位置
                new_left = 0              # left邊限制在邊界
                new_width = fixed_right - new_left
                self.w_ratio = min(1.0, new_width)  # 約束寬度
                self.cx_ratio = new_left + self.w_ratio / 2  # 重新計算中心
                adjusted = True
                
        elif handle_type in ['right', 'top-right', 'bottom-right']:
            # 拖曳右邊：如果右邊越界，固定左邊位置，調整右邊到邊界
            if right_edge > 1.0:
                fixed_left = left_edge     # 固定left邊位置  
                new_right = 1.0            # right邊限制在邊界
                new_width = new_right - fixed_left
                self.w_ratio = min(1.0, new_width)  # 約束寬度
                self.cx_ratio = fixed_left + self.w_ratio / 2  # 重新計算中心
                adjusted = True
                
        if handle_type in ['top', 'top-left', 'top-right']:
            # 拖曳上邊：如果上邊越界，固定下邊位置，調整上邊到邊界
            if top_edge < 0:
                fixed_bottom = bottom_edge  # 固定bottom邊位置
                new_top = 0                 # top邊限制在邊界
                new_height = fixed_bottom - new_top
                self.h_ratio = min(1.0, new_height)  # 約束高度
                self.cy_ratio = new_top + self.h_ratio / 2  # 重新計算中心
                adjusted = True
                
        elif handle_type in ['bottom', 'bottom-left', 'bottom-right']:
            # 拖曳下邊：如果下邊越界，固定上邊位置，調整下邊到邊界
            if bottom_edge > 1.0:
                fixed_top = top_edge        # 固定top邊位置
                new_bottom = 1.0            # bottom邊限制在邊界
                new_height = new_bottom - fixed_top  
                self.h_ratio = min(1.0, new_height)  # 約束高度
                self.cy_ratio = fixed_top + self.h_ratio / 2  # 重新計算中心
                adjusted = True
        
        if adjusted:
            DEBUG("Applied boundary constraint for {}", handle_type)

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

    def get_handle_type_at_position(self, x, y, canvas_width, canvas_height, handle_size=10):
        """
        Identify which resize handle is at the given position
        
        Args:
            x (float): Click X coordinate (canvas pixels)
            y (float): Click Y coordinate (canvas pixels)
            canvas_width (int): Canvas width
            canvas_height (int): Canvas height
            handle_size (int): Handle size (default: 10 pixels)
            
        Returns:
            str: Handle type string ("top-left", "top", etc.) or None
        """
        # Get bounding box coordinates
        x1, y1, x2, y2 = convert_label_to_canvas_coords(self, canvas_width, canvas_height)
        
        # Calculate midpoints
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        half_size = handle_size / 2
        
        # Check each handle position and return type
        if (x1 - half_size <= x <= x1 + half_size and y1 - half_size <= y <= y1 + half_size):
            return "top-left"
        elif (mid_x - half_size <= x <= mid_x + half_size and y1 - half_size <= y <= y1 + half_size):
            return "top"
        elif (x2 - half_size <= x <= x2 + half_size and y1 - half_size <= y <= y1 + half_size):
            return "top-right"
        elif (x2 - half_size <= x <= x2 + half_size and mid_y - half_size <= y <= mid_y + half_size):
            return "right"
        elif (x2 - half_size <= x <= x2 + half_size and y2 - half_size <= y <= y2 + half_size):
            return "bottom-right"
        elif (mid_x - half_size <= x <= mid_x + half_size and y2 - half_size <= y <= y2 + half_size):
            return "bottom"
        elif (x1 - half_size <= x <= x1 + half_size and y2 - half_size <= y <= y2 + half_size):
            return "bottom-left"
        elif (x1 - half_size <= x <= x1 + half_size and mid_y - half_size <= y <= mid_y + half_size):
            return "left"
        
        return None
    
    def is_on_resize_handle(self, x, y, canvas_width, canvas_height, handle_size=10):
        """
        檢測點擊是否在 resize handle 上
        現在總是檢查所有 8 個 handles
        
        Args:
            x (float): 點擊的 X 座標 (canvas 像素)
            y (float): 點擊的 Y 座標 (canvas 像素)
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
            handle_size (int): Handle 尺寸 (default: 10 pixels)
            
        Returns:
            bool: 如果在 resize handle 上返回 True，否則返回 False
        """
        # Simply check if any handle type exists at position
        return self.get_handle_type_at_position(x, y, canvas_width, canvas_height, handle_size) is not None

    def resize_by_delta(self, dx, dy, canvas_width, canvas_height, handle_type=None):
        """
        根據滑鼠拖拽增量和 handle 類型調整大小
        
        Args:
            dx (float): X 方向增量 (canvas 像素)
            dy (float): Y 方向增量 (canvas 像素)
            canvas_width (int): Canvas 寬度
            canvas_height (int): Canvas 高度
            handle_type (str): Handle 類型 ("top-left", "top", "top-right", etc.)
        """
        # 轉換為 canvas 座標
        x1, y1, x2, y2 = convert_label_to_canvas_coords(self, canvas_width, canvas_height)
        
        # 根據 handle 類型調整不同的邊界
        new_x1, new_y1, new_x2, new_y2 = x1, y1, x2, y2
        
        if handle_type == "top-left":
            # 固定右下角，調整左上角
            new_x1 = x1 + dx
            new_y1 = y1 + dy
        elif handle_type == "top":
            # 固定底邊，調整頂邊
            new_y1 = y1 + dy
        elif handle_type == "top-right":
            # 固定左下角，調整右上角
            new_x2 = x2 + dx
            new_y1 = y1 + dy
        elif handle_type == "right":
            # 固定左邊，調整右邊
            new_x2 = x2 + dx
        elif handle_type == "bottom-right":
            # 固定左上角，調整右下角
            new_x2 = x2 + dx
            new_y2 = y2 + dy
        elif handle_type == "bottom":
            # 固定頂邊，調整底邊
            new_y2 = y2 + dy
        elif handle_type == "bottom-left":
            # 固定右上角，調整左下角
            new_x1 = x1 + dx
            new_y2 = y2 + dy
        elif handle_type == "left":
            # 固定右邊，調整左邊
            new_x1 = x1 + dx
        else:
            # 預設行為：調整右下角（相容舊代碼）
            new_x2 = x2 + dx
            new_y2 = y2 + dy
        
        # 確保不會創建負尺寸的框
        min_size = 5
        if new_x2 <= new_x1:
            if handle_type in ["left", "top-left", "bottom-left"]:
                new_x1 = new_x2 - min_size
            else:
                new_x2 = new_x1 + min_size
        if new_y2 <= new_y1:
            if handle_type in ["top", "top-left", "top-right"]:
                new_y1 = new_y2 - min_size
            else:
                new_y2 = new_y1 + min_size
        
        # 計算新的中心點和尺寸
        new_cx = (new_x1 + new_x2) / 2
        new_cy = (new_y1 + new_y2) / 2
        new_width = new_x2 - new_x1
        new_height = new_y2 - new_y1
        
        # 更新 YOLO 格式的座標
        self.cx_ratio = new_cx / canvas_width
        self.cy_ratio = new_cy / canvas_height
        self.w_ratio = new_width / canvas_width
        self.h_ratio = new_height / canvas_height
        
        # 應用resize專用邊界約束，避免改變正在調整的邊界
        self.apply_resize_boundary_constraints(canvas_width, canvas_height, handle_type)
        
        DEBUG("Resized by {}", handle_type)


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
                        
                        label = LabelObject(class_id, cx_ratio, cy_ratio, w_ratio, h_ratio, line_index = line_num -1)
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

    # 為每個label設定對應的line_index
    for i, label in enumerate(sorted_labels):
        label.line_index = i
    
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

# 將YOLO格式的標籤轉換為邊界框
def yolo_to_box(xc, yc, w, h):
    x1 = xc - w/2
    y1 = yc - h/2
    x2 = xc + w/2
    y2 = yc + h/2
    area = w * h
    return (x1, y1, x2, y2, area)

def is_overlap(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, (x2 - x1)) * max(0, (y2 - y1))
    area1 = box1[4]
    area2 = box2[4]

    if intersection == 0:
        return False
    elif intersection / area1 > MAX_OVERLAP or intersection / area2 > MAX_OVERLAP: # 判斷重疊面積是否大於50%
        return True
    else:
        return False

def check_labels_horizontal_overlap(labels):
    from itertools import combinations

    has_problem = False
    for labelj, labelk in combinations(labels, 2):
        box1 = yolo_to_box(labelj.cx_ratio, labelj.cy_ratio, labelj.w_ratio, labelj.h_ratio)
        box2 = yolo_to_box(labelk.cx_ratio, labelk.cy_ratio, labelk.w_ratio, labelk.h_ratio)


        if is_overlap(box1, box2):
            has_problem = True
    return has_problem