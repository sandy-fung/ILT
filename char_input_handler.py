from Words_Label_mapping import get_class_id
from log_levels import ERROR, DEBUG

def convert_text_to_class_ids(text):
    """
    Convert a string of text into a list of class IDs
    Ignore space and hyphen
    """
    class_ids = []
    for char in text:
        if char in ("-", " "):
            continue
        class_id = get_class_id(char.upper())

        if class_id is not None:
            class_ids.append(class_id)
        else:
            DEBUG("Character '{}' not found in label mapping.", char)
        
    DEBUG("Converted text '{}' to class IDs: {}", text, class_ids)
    return class_ids
    
def is_same_length_as_labels(class_ids, label_count):
    """ Validate the length of class_ids corresponds to the number of labels """
    if len(class_ids) != label_count:
        ERROR("Input length ({}) does not match label count ({}).", len(class_ids), label_count)
        return False
    return True