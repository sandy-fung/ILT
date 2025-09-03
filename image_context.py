from dataclasses import dataclass

@dataclass
class ImageContext:
    img_w: int
    img_h: int
    disp_w: int
    disp_h: int
    ox: float
    oy: float
    sx: float   # disp_w / img_w
    sy: float   # disp_h / img_h
