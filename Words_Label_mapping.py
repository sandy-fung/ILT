# words_label_mapping.py

# 定義固定的標籤順序
LABELS = [ "0","1", "2","3", "4", "5", "6", "7","8", "9",
          "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
          "K", "L", "M", "N", "O" ,"P", "Q", "R", "S", "T",
          "U", "V", "W", "X", "Y","Z"]
# LABELS = ["0", "8","B", "O" , "D", "Q"]
def get_labels():
    """返回標籤列表"""
    return LABELS
# 建立映射：label → class_id（0-based）
label_to_class = {label: i for i, label in enumerate(LABELS)}
class_to_label = {i: label for i, label in enumerate(LABELS)}

# 可選：提供查詢函數（可用於防呆）
def get_class_id(label):
    return label_to_class.get(label)

def get_label(class_id):
    return class_to_label.get(class_id)

#sequenctial class id, insteadof ascci
def get_labels():
    new_labels = [get_label(class_id) for class_id in class_to_label.keys()]
    return new_labels


# === ASCII 對應版本 ===
ascii_label_to_class = {label: ord(label) for label in LABELS}
ascii_class_to_label = {ord(label): label for label in LABELS}

def get_ascii_class_id(label):
    print(f"DEBUG: input label = {label} (type={type(label)})")
    return ascii_label_to_class.get(label)

def get_ascii_label(class_id):
    return ascii_class_to_label.get(class_id)