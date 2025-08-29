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

def get_original_filename_from_crop(crop_stem: str) -> str:
    """
    從crop檔案名稱推導原始檔案名稱
    
    Args:
        crop_stem: crop檔案的stem (無副檔名)
        例如: "3109Q_frame_20250624_072650_00000001_1" -> "frame_20250624_072650_00000001"
        例如: "227103_output_20250726_091833A_20250728_140924_235_0" -> "output_20250726_091833A_20250728_140924_235"
    
    Returns:
        str: 原始檔案名稱
    """
    # 首先處理 _crop_ 模式
    if '_crop_' in crop_stem:
        crop_stem = crop_stem.split('_crop_')[0]
    
    # 移除末尾的 _數字 (如 _0, _1 等)
    parts = crop_stem.rsplit('_', 1)
    if len(parts) > 1 and parts[1].isdigit():
        crop_stem = parts[0]
    
    # 識別並移除車牌號前綴
    # 車牌號模式：在 frame_ 或 output_ 之前的字母數字組合
    if '_frame_' in crop_stem:
        # 例：3109Q_frame_xxx → frame_xxx
        idx = crop_stem.find('_frame_')
        if idx > 0:
            return crop_stem[idx+1:]  # 從 frame_ 開始保留
    elif '_output_' in crop_stem:
        # 例：227103_output_xxx → output_xxx
        idx = crop_stem.find('_output_')
        if idx > 0:
            return crop_stem[idx+1:]  # 從 output_ 開始保留
    
    return crop_stem

def find_original_image_path(crop_image_path: str) -> str:
    """
    從crop圖片路徑找到對應的原始圖片路徑
    
    Args:
        crop_image_path: crop圖片的完整路徑
    
    Returns:
        str: 原始圖片的完整路徑，如果找不到則返回空字串
    """
    crop_dir = os.path.dirname(crop_image_path)
    crop_filename = os.path.basename(crop_image_path)
    crop_stem = os.path.splitext(crop_filename)[0]
    crop_ext = os.path.splitext(crop_filename)[1]
    
    # 推導原始檔案名
    original_stem = get_original_filename_from_crop(crop_stem)
    original_filename = original_stem + crop_ext
    
    # 找到原始圖片目錄（從crop目錄往上一層，然後進入images目錄）
    parent_dir = os.path.dirname(crop_dir)
    original_dir = os.path.join(parent_dir, "images")
    original_path = os.path.join(original_dir, original_filename)
    
    # 檢查檔案是否存在
    if os.path.exists(original_path):
        DEBUG("Found original image for crop: {} -> {}", crop_image_path, original_path)
        return original_path
    else:
        DEBUG("Original image not found for crop: {}, expected: {}", crop_image_path, original_path)
        return ""

def find_original_label_path(original_image_path: str) -> str:
    """
    從原圖路徑找到對應的標註檔路徑
    
    Args:
        original_image_path: 原圖的完整路徑
    
    Returns:
        str: 標註檔的完整路徑，如果找不到則返回空字串
    """
    if not original_image_path:
        return ""
    
    # 取得原圖目錄、檔名和副檔名
    image_dir = os.path.dirname(original_image_path)
    image_filename = os.path.basename(original_image_path)
    image_stem = os.path.splitext(image_filename)[0]
    
    # 找到標註目錄（從images目錄對應到labels目錄）
    parent_dir = os.path.dirname(image_dir)
    label_dir = os.path.join(parent_dir, "labels")
    
    # 構建標註檔路徑（與圖片同名但副檔名為.txt）
    label_filename = image_stem + ".txt"
    label_path = os.path.join(label_dir, label_filename)
    
    # 檢查檔案是否存在
    if os.path.exists(label_path):
        DEBUG("Found original label for image: {} -> {}", original_image_path, label_path)
        return label_path
    else:
        DEBUG("Original label not found for image: {}, expected: {}", original_image_path, label_path)
        return ""