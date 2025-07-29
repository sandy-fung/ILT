import tkinter as tk
from tkinter import filedialog
from UI_event import UIEvent
from log_levels import DEBUG, INFO, ERROR
from tkinter import messagebox
import label_display_utils
import bbox_controller
from settings_dialog import SettingsDialog
import config_utils
import Words_Label_mapping as wlm
from outline_font import draw_outlined_text
from constants import VERSION_NUM


DEFAULT_W = 1920
DEFAULT_H = 1080
class UI:
    def __init__(self):
        self.dispatch = None
        width, height = config_utils.get_window_size()
        print(f"Window size from config: {width}x{height}")
        if  width is not None and height is not None:
            self.window_width = width
            self.window_height = height
        else:
            self.window_width = DEFAULT_W
            self.window_height = DEFAULT_H


        # Create the main window
        self.window = tk.Tk()
        self.window.title("Image Labelling Tool")

        # set windows to saved size and position
        x,y = config_utils.get_window_position()
        if  x is not None and y is not None:
            self.window_x = x
            self.window_y = y
            self.window.geometry(f"{self.window_width}x{self.window_height}+{self.window_x}+{self.window_y}")
        else:
            self.window.geometry(f"{self.window_width}x{self.window_height}")

        # Ensure window can receive keyboard focus
        self.window.focus_set()
        self.window.focus_force()

        # Initialize drawing-related states
        self.bbox_controller = None
        self.drawing_mode = False
        
        # Initialize options
        self.original_image = None

        # Load UI settings from config
        self.SHOW_CLASS_ID_BUTTONS = config_utils.get_show_class_id_buttons()
        self.SHOW_TEXT_BOX = config_utils.get_show_text_box()
        self.SHOW_PREVIEW = config_utils.get_show_preview()
        self.SHOW_INPUT_BOX = config_utils.get_show_input_box()
        self.LABEL_FONT_SIZE = config_utils.get_ui_label_font_size_in_config()

        self.setup_ui()
        self.setup_events()

    def set_dispatcher(self, event_dispatcher):
        self.dispatch = event_dispatcher

# Define UI components
    def setup_ui(self):
        self.create_top_area()
        self.create_middle_area()
        self.create_bottom_area()

    def create_top_area(self):
        self.toolbar =  tk.Frame(self.window, bg = "#F4F4F4")
        self.toolbar.pack(side = "top", fill = "x")

        self.reselect_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 16, height = 1,
            text = "Reselect Folders", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_bt_click_reselect
        )
        self.reselect_button.pack(side = "left", padx = 5)
        
        self.crop_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 4, height = 1,
            text = "Crop", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_bt_click_crop
        )
        self.crop_button.pack(side = "left")
        
        self.add_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 4, height = 1,
            text = "Add", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_bt_click_add
        )
        self.add_button.pack(side = "left", padx = 5)

        self.del_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 4, height = 1,
            text="Delete", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_delete_image_button)
        self.del_button.pack(side = "left", padx = 5)
        
        self.mov_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 8, height = 1,
            text="Move to", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_move_image_button)
        self.mov_button.pack(side = "left", padx = 5)
        

        self.configuration_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 12, height = 1,
            text = "Configuration", fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_configuration_click
        )
        self.configuration_button.pack(side = "left", padx = 5)

        self.info_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 4, height = 1,
            text="Info", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.show_info_menu)
        self.info_button.pack(side = "left", padx =0)
        
         # 建立 version menu，但暫不顯示
        self.info_menu = tk.Menu(self.window, tearoff=0)
        self.info_menu.add_command(label="version-"+VERSION_NUM)


    def create_middle_area(self):
        self.middle_frame = tk.Frame(self.window)
        self.middle_frame.pack(side = "top", fill = "both", expand = True)

        self.create_canvas()
        
        # Initialize drawing controller
        self.bbox_controller = bbox_controller.BBoxController(self.canvas)

        # Create context menu
        self.create_context_menu()

    def create_canvas(self):
        self.canvas_frame = tk.Frame(self.middle_frame)
        self.canvas_frame.pack(side = "left", fill = "both", expand = True)
        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness = 0)
        self.canvas.pack(fill = "both", expand = True)


    def create_bottom_area(self):
        self.bottom_frame = tk.Frame(self.window, relief = "ridge", bd = 2, bg = "#FAFAFA")
        self.bottom_frame.pack(side = "bottom", fill = "x")


        self.create_text_area()

        self.create_hint_area()
        self.create_preview_area()

    def create_text_area(self):
        self.text_frame = tk.Frame(self.bottom_frame, bg = "#FAFAFA")
        self.text_frame.pack(side = "left", fill = "both", expand = True)

        # Initialize input box if enabled
        if self.SHOW_INPUT_BOX:
            self.input_box = tk.Entry(self.text_frame, font = ("Segoe UI", 11), fg = "#8E8E79")
            self.input_box.pack(side = "top", expand = True, fill  = "x", padx = 20, pady = 10)

            self.input_box.insert(0, "請輸入車牌號碼")
            self.input_box.bind("<FocusIn>", self._on_input_focus_in)
            self.input_box.bind("<FocusOut>", self._on_input_focus_out)

            self.input_box.bind("<Return>", self.input_enter)
            self.input_box.bind("<KeyRelease>", self.force_uppercase)

        else:
            DEBUG("Input box is not shown as per configuration.")
            self.input_box = None

        # Initialize text box if enabled
        if self.SHOW_TEXT_BOX:
            self.text_box = tk.Text(
                self.text_frame,
                height = 15, bg = "white",
                font = ("Segoe UI", 11), fg = "#2d2d2d",
                relief = "sunken",
                wrap = "word"
            )
            self.text_box.tag_configure("left", justify = "left")
            self.text_box.pack(side = "top", fill = "x", expand = True, padx = 20, pady = 10)
            self.text_box.bind("<<Modified>>", self.on_text_modified)

        else:
            DEBUG("Text box is not shown as per configuration.")
            self.text_box = None
        

    def create_hint_area(self):
        self.hint_frame = tk.Frame(self.bottom_frame, bg = "#FAFAFA")
        self.hint_frame.pack(side = "left", expand = True, fill = "y", pady = (0, 10))

        hint_text = (
            "← 上一張\n"
            "→ 下一張\n"
            "滑鼠左鍵：選取box\n"
            "拖曳選中的box：移動box位置\n"
            "拖曳右下角灰色方塊：調整box大小\n"
            "滑鼠右鍵：刪除選中的box\n"
            "Delete鍵：刪除選中的box\n"
            "Ctrl：切換繪框模式\n"
            "繪框模式下拖拽：繪製新box\n"
            "※ 標籤會自動依位置排序"
            )
        self.hint_label = tk.Label(
            self.hint_frame,
            width = 50, height = 10, bg = "#FAFAFA",
            text = hint_text, justify = "left", anchor = "w", fg = "#2d2d2d", font = ("Segoe UI", 10)
        )
        self.hint_label.grid(row = 1, column = 0, columnspan = 2, sticky = "s", pady = (10, 0))
        self.index_label = tk.Label(self.hint_frame, bg = "#FAFAFA", text = " : ", fg = "#C0C00C", font = ("Segoe UI", 11))
        self.index_label.grid(row = 0, column = 2, sticky = "nwse")


    # Add drawing mode status display
        self.drawing_mode_label = tk.Label(
            self.hint_frame, bg = "#FAFAFA", text = "普通模式", 
            fg = "#8E8E79", font = ("Segoe UI", 11)
        )
        self.drawing_mode_label.grid(row = 0, column = 0, sticky = "nw")
        
        # Add selection status display
        self.selection_status_label = tk.Label(
            self.hint_frame, bg = "#FAFAFA", text = "未選中任何框", 
            fg = "#8E8E79", font = ("Segoe UI", 11)
        )
        self.selection_status_label.grid(row = 0, column = 1, sticky = "nw", padx = (20, 0))

    def create_preview_area(self):
        if not self.SHOW_PREVIEW:
            DEBUG("Preview area is not shown as per configuration.")
            return
            
        # Create preview frame with border
        self.preview_frame = tk.Frame(self.bottom_frame, bg = "#FAFAFA", relief = "ridge", bd = 2)
        self.preview_frame.pack(side = "right", fill = "both", expand = True)
        
        # Set minimum size for preview frame
        self.preview_frame.update_idletasks()
        self.preview_frame.configure(width=250, height=250)
        
        # Add title label
        self.preview_title = tk.Label(
            self.preview_frame, 
            text = "原尺寸預覽", 
            bg = "#FAFAFA", 
            fg = "#2d2d2d", 
            font = ("Segoe UI", 11, "bold")
        )
        self.preview_title.pack(side = "top", pady = 5)
        
        # Create preview canvas container
        self.preview_canvas_frame = tk.Frame(self.preview_frame, bg = "#FAFAFA")
        self.preview_canvas_frame.pack(side = "top", fill = "both", expand = True, padx = 10, pady = (0, 10))
        
        # Create scrollbars
        self.preview_v_scrollbar = tk.Scrollbar(self.preview_canvas_frame, orient = "vertical")
        self.preview_h_scrollbar = tk.Scrollbar(self.preview_canvas_frame, orient = "horizontal")
        
        # Create preview canvas with dynamic size
        self.preview_canvas = tk.Canvas(
            self.preview_canvas_frame,
            bg = "white",
            highlightthickness = 1,
            highlightbackground = "#8E8E79",
            yscrollcommand = self.preview_v_scrollbar.set,
            xscrollcommand = self.preview_h_scrollbar.set
        )
        
        # Configure scrollbars
        self.preview_v_scrollbar.config(command = self.preview_canvas.yview)
        self.preview_h_scrollbar.config(command = self.preview_canvas.xview)
        
        # Pack canvas and scrollbars
        self.preview_canvas.grid(row = 0, column = 0, sticky = "nsew")
        self.preview_v_scrollbar.grid(row = 0, column = 1, sticky = "ns")
        self.preview_h_scrollbar.grid(row = 1, column = 0, sticky = "ew")
        
        # Configure grid weights
        self.preview_canvas_frame.grid_rowconfigure(0, weight = 1)
        self.preview_canvas_frame.grid_columnconfigure(0, weight = 1)
        
        # Initialize preview state
        self.preview_image = None
        self.preview_photo_image = None
        
        # Schedule placeholder text after window is rendered
        if self.preview_canvas:
            self.preview_canvas.after_idle(self._add_preview_placeholder)

        # Bind magnifier events to preview canvas
        if self.preview_canvas:
            self.preview_canvas.bind("<Enter>", self.on_preview_enter)
            self.preview_canvas.bind("<Leave>", self.on_preview_leave)
            self.preview_canvas.bind("<Button-1>", self.on_preview_left_click)
            self.preview_canvas.bind("<Button-3>", self.on_preview_right_drag_start)
            self.preview_canvas.bind("<B3-Motion>", self.on_preview_right_drag)
            self.preview_canvas.bind("<ButtonRelease-3>", self.on_preview_right_drag_end)
        
        # Initialize magnifier state
        self.magnifier_tooltip = None
        self.is_dragging_preview = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Initialize magnifier cache (LRU cache for magnified regions) 
        self.magnifier_cache = {}
        self.cache_access_order = []
        
        # Load magnifier configuration
        self.load_magnifier_config()
    
    def _add_preview_placeholder(self):
        """Add placeholder text to preview canvas after it has been rendered"""
        if not self.preview_canvas:
            return
            
        # Get actual canvas dimensions
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Add placeholder text at center
        self.preview_canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text = "尚未載入圖片",
            fill = "#8E8E79",
            font = ("Segoe UI", 12),
            tags = "placeholder"
        )

    def load_magnifier_config(self):
        """Load magnifier configuration from config file"""
        try:
            import config_utils
            
            self.magnifier_enabled = config_utils.get_magnifier_enabled()
            self.magnifier_zoom_factor = config_utils.get_magnifier_zoom_factor()
            self.magnifier_tooltip_size = config_utils.get_magnifier_tooltip_size()
            self.magnifier_cursor_type = config_utils.get_magnifier_cursor_type()
            self.magnifier_region_size = config_utils.get_magnifier_region_size()
            self.max_cache_size = config_utils.get_magnifier_cache_size()
            
            # Set magnifier cursor based on configuration
            self.magnifier_cursor = self.get_magnifier_cursor()
            
            DEBUG("Magnifier config loaded: enabled={}, zoom={}, tooltip_size={}, cursor={}, region_size={}, cache_size={}", 
                  self.magnifier_enabled, self.magnifier_zoom_factor, self.magnifier_tooltip_size,
                  self.magnifier_cursor_type, self.magnifier_region_size, self.max_cache_size)
                  
        except Exception as e:
            # Use defaults if config loading fails
            ERROR("Failed to load magnifier config: {}, using defaults", str(e))
            self.magnifier_enabled = True
            self.magnifier_zoom_factor = 3.0
            self.magnifier_tooltip_size = 200
            self.magnifier_cursor_type = "target"
            self.magnifier_region_size = 50
            self.max_cache_size = 10
            self.magnifier_cursor = self.get_magnifier_cursor()
            
    def get_magnifier_cursor(self):
        """Get appropriate magnifier cursor based on configuration"""
        cursor_options = {
            "target": "target",           # 🎯 Target/crosshair - looks like magnifier focus
            "dotbox": "dotbox",           # ⚈ Dotted box - frame-like
            "tcross": "tcross",           # ✚ Thick cross - precision tool  
            "crosshair": "crosshair",     # + Thin crosshair - classic precision
            "plus": "plus",               # ➕ Plus sign - zoom indication
            "circle": "circle",           # ○ Circle - magnifier lens shape
            "sizing": "sizing"            # ⚏ Original option (fallback)
        }
        
        # Get configured cursor type
        cursor_type = cursor_options.get(self.magnifier_cursor_type, "target")
        
        DEBUG("Selected magnifier cursor: {} -> {}", self.magnifier_cursor_type, cursor_type)
        return cursor_type
        
    def set_magnifier_cursor_type(self, cursor_type):
        """Dynamically change magnifier cursor type (for testing different options)
        
        Args:
            cursor_type: One of: "target", "dotbox", "tcross", "crosshair", "plus", "circle", "sizing"
        """
        self.magnifier_cursor_type = cursor_type
        self.magnifier_cursor = self.get_magnifier_cursor()
        
        # Update cursor immediately if mouse is over preview canvas
        if hasattr(self, 'preview_canvas') and self.preview_canvas:
            try:
                self.preview_canvas.config(cursor=self.magnifier_cursor)
                DEBUG("Magnifier cursor updated to: {}", cursor_type)
            except:
                pass

    def set_original_image(self, original_image):
        """Set the original image reference for preview functionality
        
        Args:
            original_image: OpenCV image (numpy array)
        """
        self.original_image = original_image
        # Clear magnifier cache when image changes
        self.clear_magnifier_cache()
        DEBUG("Original image reference updated for preview")

    def update_preview(self, original_image):
        """Update preview with the full original image
        
        Args:
            original_image: PIL Image object
        """
        if not self.SHOW_PREVIEW or self.preview_canvas is None:
            return
            
        from PIL import Image, ImageTk
        
        # Clear magnifier cache when preview updates
        self.clear_magnifier_cache()
        
        # Clear previous preview
        self.preview_canvas.delete("all")
        
        # Get original image dimensions
        img_width, img_height = original_image.size
        
        # Convert to PhotoImage for Tkinter (original size)
        self.preview_photo_image = ImageTk.PhotoImage(original_image)
        
        # Display on preview canvas at original size
        self.preview_canvas.create_image(0, 0, anchor = "nw", image = self.preview_photo_image, tags = "preview_image")
        
        # Update scroll region to match original image size
        self.preview_canvas.config(scrollregion = (0, 0, img_width, img_height))
        
        # Get canvas dimensions for info text positioning
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Add info text at visible position
        info_text = f"原始尺寸: {img_width}×{img_height}"
        self.preview_canvas.create_text(
            10, canvas_height - 5,
            text = info_text,
            fill = "#8E8E79",
            font = ("Segoe UI", 9),
            anchor = "sw",
            tags = ("info_text", "overlay")
        )
        
        DEBUG("Preview updated with original size image: {}×{}", img_width, img_height)

    def clear_preview(self):
        """Clear the preview canvas"""
        if not self.SHOW_PREVIEW or self.preview_canvas is None:
            return
            
        # Hide any visible magnifier tooltip
        self.hide_magnifier_tooltip()
        
        # Clear magnifier cache
        self.clear_magnifier_cache()
            
        # Delete all items
        self.preview_canvas.delete("all")
        
        # Get current canvas dimensions
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Show placeholder text at center
        self.preview_canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text = "尚未載入圖片",
            fill = "#8E8E79",
            font = ("Segoe UI", 12),
            tags = "placeholder"
        )
        
        # Reset scroll region to canvas size
        self.preview_canvas.config(scrollregion = (0, 0, canvas_width, canvas_height))
        
        # Clear stored references
        self.preview_photo_image = None
    

    # Magnifier functionality for preview panel
    def on_preview_enter(self, event):
        """Handle mouse enter event on preview canvas - change cursor to magnifier"""
        if not self.SHOW_PREVIEW or self.preview_canvas is None or not self.magnifier_enabled:
            return
            
        DEBUG("Mouse entered preview canvas")
        self.preview_canvas.config(cursor=self.magnifier_cursor)
        
    def on_preview_leave(self, event):
        """Handle mouse leave event on preview canvas - restore normal cursor"""
        if not self.SHOW_PREVIEW or self.preview_canvas is None:
            return
            
        DEBUG("Mouse left preview canvas")
        self.preview_canvas.config(cursor="")
        
        # Hide magnifier tooltip if visible
        self.hide_magnifier_tooltip()
        
    def on_preview_left_click(self, event):
        """Handle left click on preview canvas - show magnified tooltip"""
        if not self.SHOW_PREVIEW or self.preview_canvas is None or self.original_image is None or not self.magnifier_enabled:
            return
            
        DEBUG("Left click on preview canvas at ({}, {})", event.x, event.y)
        
        # Hide existing tooltip first
        self.hide_magnifier_tooltip()
        
        # Show magnifier tooltip at clicked position
        self.show_magnifier_tooltip(event.x, event.y)
        
    def show_magnifier_tooltip(self, canvas_x, canvas_y):
        """Create and show magnifier tooltip with 3x zoomed region
        
        Args:
            canvas_x, canvas_y: Click position on preview canvas
        """
        if not self.original_image:
            DEBUG("No original image available for magnification")
            return
            
        try:
            from PIL import Image, ImageTk
            
            # Convert canvas coordinates to original image coordinates
            img_x, img_y = self.canvas_to_image_coords(canvas_x, canvas_y)
            if img_x is None or img_y is None:
                DEBUG("Invalid coordinates for magnification")
                return
                
            # Extract magnified region from original image using configured parameters
            magnified_image = self.extract_magnified_region(
                img_x, img_y, 
                zoom_factor=self.magnifier_zoom_factor,
                region_size=self.magnifier_region_size
            )
            if magnified_image is None:
                DEBUG("Failed to extract magnified region")
                return
                
            # Create tooltip window
            self.magnifier_tooltip = tk.Toplevel(self.window)
            self.magnifier_tooltip.wm_overrideredirect(True)  # Remove window decorations
            self.magnifier_tooltip.configure(bg="black", bd=2, relief="solid")
            
            # Create label for magnified image
            tooltip_label = tk.Label(self.magnifier_tooltip, image=magnified_image, bg="black")
            tooltip_label.pack()
            
            # Calculate tooltip position to avoid screen edges
            tooltip_x, tooltip_y = self.calculate_tooltip_position(canvas_x, canvas_y)
            self.magnifier_tooltip.geometry(f"+{tooltip_x}+{tooltip_y}")
            
            # Store image reference to prevent garbage collection
            self.magnifier_tooltip.image = magnified_image
            
            DEBUG("Magnifier tooltip shown at canvas position ({}, {}) -> image position ({}, {})", 
                  canvas_x, canvas_y, img_x, img_y)
                  
            # Dispatch magnifier show event
            if self.dispatch:
                self.dispatch(UIEvent.MAGNIFIER_SHOW, {
                    "canvas_x": canvas_x,
                    "canvas_y": canvas_y,
                    "image_x": img_x,
                    "image_y": img_y
                })
                  
        except Exception as e:
            ERROR("Failed to show magnifier tooltip: {}", str(e))
            
    def hide_magnifier_tooltip(self):
        """Hide magnifier tooltip if visible"""
        if self.magnifier_tooltip:
            try:
                self.magnifier_tooltip.destroy()
                self.magnifier_tooltip = None
                DEBUG("Magnifier tooltip hidden")
                
                # Dispatch magnifier hide event
                if self.dispatch:
                    self.dispatch(UIEvent.MAGNIFIER_HIDE, {})
            except:
                pass
                
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Convert preview canvas coordinates to original image coordinates
        
        Args:
            canvas_x, canvas_y: Coordinates on preview canvas
            
        Returns:
            tuple: (img_x, img_y) in original image coordinates, or (None, None) if invalid
        """
        if not self.original_image or not self.preview_photo_image:
            return None, None
            
        try:
            # Get original image dimensions
            img_width, img_height = self.original_image.size
            
            # Since image is displayed at original size, we need to account for scrolling
            # Convert canvas coordinates to window coordinates
            canvas_x_scroll = self.preview_canvas.canvasx(canvas_x)
            canvas_y_scroll = self.preview_canvas.canvasy(canvas_y)
            
            # Direct mapping since no scaling
            img_x = int(canvas_x_scroll)
            img_y = int(canvas_y_scroll)
            
            # Check if coordinates are within image bounds
            if img_x < 0 or img_y < 0 or img_x >= img_width or img_y >= img_height:
                return None, None
            
            # Clamp to image bounds
            img_x = max(0, min(img_width - 1, img_x))
            img_y = max(0, min(img_height - 1, img_y))
            
            return img_x, img_y
            
        except Exception as e:
            ERROR("Failed to convert canvas coordinates to image coordinates: {}", str(e))
            return None, None
            
    def extract_magnified_region(self, center_x, center_y, zoom_factor=3.0, region_size=50):
        """Extract and magnify a region from original image with caching
        
        Args:
            center_x, center_y: Center point in original image coordinates
            zoom_factor: Magnification factor (default 3x)
            region_size: Size of region to extract in pixels
            
        Returns:
            ImageTk.PhotoImage: Magnified region image, or None if failed
        """
        if not self.original_image:
            return None
            
        # Generate cache key based on position and parameters
        cache_key = f"{center_x}_{center_y}_{zoom_factor}_{region_size}_{id(self.original_image)}"
        
        # Check cache first
        cached_result = self.get_from_magnifier_cache(cache_key)
        if cached_result:
            DEBUG("Using cached magnified region for key: {}", cache_key)
            return cached_result
            
        try:
            from PIL import Image, ImageTk
            
            img_width, img_height = self.original_image.size
            half_region = region_size // 2
            
            # Calculate extraction bounds with boundary checks
            left = max(0, center_x - half_region)
            top = max(0, center_y - half_region)
            right = min(img_width, center_x + half_region)
            bottom = min(img_height, center_y + half_region)
            
            # Ensure we have a valid region
            if right <= left or bottom <= top:
                ERROR("Invalid region bounds: ({}, {}) to ({}, {})", left, top, right, bottom)
                return None
            
            # Extract region efficiently
            region = self.original_image.crop((left, top, right, bottom))
            
            # Calculate magnified size
            region_width = right - left
            region_height = bottom - top
            magnified_width = max(1, int(region_width * zoom_factor))
            magnified_height = max(1, int(region_height * zoom_factor))
            
            # Use high-quality interpolation for better results
            if magnified_width > region_width or magnified_height > region_height:
                # Upscaling - use Lanczos for best quality
                resample_method = Image.Resampling.LANCZOS
            else:
                # Downscaling - use area averaging
                resample_method = Image.Resampling.LANCZOS
                
            magnified_region = region.resize(
                (magnified_width, magnified_height), 
                resample_method
            )
            
            # Convert to PhotoImage
            photo_image = ImageTk.PhotoImage(magnified_region)
            
            # Cache the result
            self.add_to_magnifier_cache(cache_key, photo_image)
            
            DEBUG("Created and cached magnified region: {}x{} -> {}x{}", 
                  region_width, region_height, magnified_width, magnified_height)
            
            return photo_image
            
        except Exception as e:
            ERROR("Failed to extract magnified region: {}", str(e))
            return None
            
    def get_from_magnifier_cache(self, cache_key):
        """Get magnified region from cache (LRU access)
        
        Args:
            cache_key: Cache key string
            
        Returns:
            ImageTk.PhotoImage or None: Cached image if found
        """
        if not self.SHOW_PREVIEW:
            return
        
        if cache_key in self.magnifier_cache:
            # Move to end of access order (most recently used)
            self.cache_access_order.remove(cache_key)
            self.cache_access_order.append(cache_key)
            return self.magnifier_cache[cache_key]
        return None
        
    def add_to_magnifier_cache(self, cache_key, photo_image):
        """Add magnified region to cache with LRU eviction
        
        Args:
            cache_key: Cache key string
            photo_image: ImageTk.PhotoImage to cache
        """
        if not self.SHOW_PREVIEW:
            return
        
        # Remove if already exists
        if cache_key in self.magnifier_cache:
            self.cache_access_order.remove(cache_key)
        
        # Add to cache
        self.magnifier_cache[cache_key] = photo_image
        self.cache_access_order.append(cache_key)
        
        # Evict least recently used if cache is full
        while len(self.cache_access_order) > self.max_cache_size:
            lru_key = self.cache_access_order.pop(0)
            if lru_key in self.magnifier_cache:
                del self.magnifier_cache[lru_key]
                DEBUG("Evicted from magnifier cache: {}", lru_key)
        
        DEBUG("Added to magnifier cache: {} (cache size: {})", 
              cache_key, len(self.cache_access_order))
              
    def clear_magnifier_cache(self):
        """Clear all cached magnified regions (called when image changes)"""
        if not self.SHOW_PREVIEW:
            return
        
        self.magnifier_cache.clear()
        self.cache_access_order.clear()
        DEBUG("Magnifier cache cleared")
            
    def calculate_tooltip_position(self, canvas_x, canvas_y):
        """Calculate optimal tooltip position to avoid screen edges
        
        Args:
            canvas_x, canvas_y: Click position on canvas
            
        Returns:
            tuple: (x, y) screen coordinates for tooltip
        """
        # Get canvas position on screen
        canvas_abs_x = self.preview_canvas.winfo_rootx()
        canvas_abs_y = self.preview_canvas.winfo_rooty()
        
        # Calculate initial tooltip position (offset from click)
        tooltip_x = canvas_abs_x + canvas_x + 20
        tooltip_y = canvas_abs_y + canvas_y + 20
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Estimate tooltip size (will be adjusted based on magnified region)
        tooltip_width = 150  # Approximate
        tooltip_height = 150
        
        # Adjust position to avoid screen edges
        if tooltip_x + tooltip_width > screen_width:
            tooltip_x = canvas_abs_x + canvas_x - tooltip_width - 20
            
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = canvas_abs_y + canvas_y - tooltip_height - 20
            
        # Ensure tooltip is not off-screen
        tooltip_x = max(0, tooltip_x)
        tooltip_y = max(0, tooltip_y)
        
        return tooltip_x, tooltip_y
        
    def on_preview_right_drag_start(self, event):
        """Handle right mouse button press - start dragging if image is larger than canvas"""
        if not self.SHOW_PREVIEW or self.preview_canvas is None or not self.is_image_draggable():
            return
            
        DEBUG("Right drag start on preview canvas at ({}, {})", event.x, event.y)
        self.is_dragging_preview = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Change cursor to indicate dragging mode
        self.preview_canvas.config(cursor="fleur")
        
        # Dispatch preview drag start event
        if self.dispatch:
            self.dispatch(UIEvent.PREVIEW_DRAG_START, {
                "x": event.x,
                "y": event.y
            })
        
    def on_preview_right_drag(self, event):
        """Handle right mouse drag - update image position"""
        if not self.is_dragging_preview or not self.SHOW_PREVIEW:
            return
            
        # Calculate drag offset
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        DEBUG("Right drag on preview canvas: dx={}, dy={}", dx, dy)
        
        # Update preview view position
        self.update_preview_view(dx, dy)
        
        # Update drag start position for next iteration
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Dispatch preview drag event
        if self.dispatch:
            self.dispatch(UIEvent.PREVIEW_DRAG, {
                "x": event.x,
                "y": event.y,
                "dx": dx,
                "dy": dy
            })
        
    def on_preview_right_drag_end(self, event):
        """Handle right mouse button release - end dragging"""
        if not self.is_dragging_preview:
            return
            
        DEBUG("Right drag end on preview canvas")
        self.is_dragging_preview = False
        
        # Restore magnifier cursor
        self.preview_canvas.config(cursor=self.magnifier_cursor)
        
        # Dispatch preview drag end event
        if self.dispatch:
            self.dispatch(UIEvent.PREVIEW_DRAG_END, {
                "x": event.x,
                "y": event.y
            })
        
    def is_image_draggable(self):
        """Check if current image is large enough to support dragging
        
        Returns:
            bool: True if image can be dragged, False otherwise
        """
        if not self.original_image or not self.preview_photo_image or not self.preview_canvas:
            return False
            
        try:
            # Get original image dimensions
            img_width, img_height = self.original_image.size
            
            # Get actual preview canvas dimensions
            self.preview_canvas.update_idletasks()
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Image is draggable if it's larger than canvas in either dimension
            draggable = img_width > canvas_width or img_height > canvas_height
            
            DEBUG("Image draggable check: {}x{} vs canvas {}x{} -> {}", 
                  img_width, img_height, canvas_width, canvas_height, draggable)
                  
            return draggable
            
        except Exception as e:
            ERROR("Failed to check if image is draggable: {}", str(e))
            return False
            
    def update_preview_view(self, dx, dy):
        """Update preview canvas view position based on drag offset
        
        Args:
            dx, dy: Drag offset in pixels
        """
        if not self.SHOW_PREVIEW or self.preview_canvas is None:
            return
            
        try:
            # Get current scroll position (0.0 to 1.0)
            current_x_top, current_x_bottom = self.preview_canvas.xview()
            current_y_top, current_y_bottom = self.preview_canvas.yview()
            
            # Calculate scroll region dimensions
            scroll_region = self.preview_canvas.cget("scrollregion").split()
            if len(scroll_region) != 4:
                return
                
            total_width = float(scroll_region[2]) - float(scroll_region[0])
            total_height = float(scroll_region[3]) - float(scroll_region[1])
            
            # Calculate canvas dimensions
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if total_width <= canvas_width and total_height <= canvas_height:
                return  # No scrolling needed
                
            # Convert drag offset to scroll ratio
            scroll_dx = -dx / total_width if total_width > canvas_width else 0
            scroll_dy = -dy / total_height if total_height > canvas_height else 0
            
            # Calculate new scroll positions
            new_x_top = max(0.0, min(1.0, current_x_top + scroll_dx))
            new_y_top = max(0.0, min(1.0, current_y_top + scroll_dy))
            
            # Apply new scroll positions
            if total_width > canvas_width:
                self.preview_canvas.xview_moveto(new_x_top)
            if total_height > canvas_height:
                self.preview_canvas.yview_moveto(new_y_top)
                
            DEBUG("Updated preview view: x={:.3f}, y={:.3f}", new_x_top, new_y_top)
            
        except Exception as e:
            ERROR("Failed to update preview view: {}", str(e))

    def show_class_id_buttons(self, var, labels):
        if self.SHOW_CLASS_ID_BUTTONS:
            DEBUG("show_class_id_buttons with var: {}, labels: {}", var, labels)
            self.class_id_frame = tk.Frame(self.middle_frame, bg = "#FAFAFA")
            self.class_id_frame.pack(side = "right", fill = "y")

            self.class_id_vars = tk.StringVar(value = var)
            for i, label in enumerate(labels):
                column = i // 13
                row = i % 13
                button = tk.Radiobutton(
                    self.class_id_frame, bg = "#FAFAFA", font = ("Segoe UI Mono", 10),
                    text = label, variable = self.class_id_vars, value = label, width = 3, anchor = "center", indicatoron = True,
                    command = lambda l = label: self.dispatch(UIEvent.CLASS_ID_CHANGE, {"label": l})
             ) if self.dispatch else None
                button.grid(row = row, column = column, padx = 5, pady = 5)

        else:
            return

# About canvas

    def get_UI_window_size(self):
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        # DEBUG("Window size: width={}, height={}", window_width, window_height)
        return window_width, window_height

    def get_UI_window_position(self):
        window_x = self.window.winfo_x()
        window_y = self.window.winfo_y()
        # DEBUG("Window position: x={}, y={}", window_x, window_y)
        return window_x, window_y

    def get_canvas_size(self):
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        DEBUG("Canvas size: height: {}, width: {}", self.canvas_height, self.canvas_width)
        if self.canvas_height == 0 or self.canvas_width == 0:
            self.canvas_height = 720
            self.canvas_width = 1920
        return self.canvas_height, self.canvas_width
    
    def on_canvas_resize(self, event):
        if self.dispatch:
            self.dispatch(UIEvent.CANVAS_RESIZE, {})

    def update_image_canvas(self, image):
        DEBUG("update_image_canvas")
        self.canvas.delete("all")
        self.canvas.image = image
        self.canvas.create_image(self.canvas_width//2, self.canvas_height//2, anchor = "center", image = image)
        DEBUG("Image updated on canvas with height: {}, width: {}", self.canvas_height, self.canvas_width)

    def clear_all_labels_canvas(self):
        """Clear all items on the canvas"""
        # DEBUG("Clearing all items on canvas")
        all_items = self.canvas.find_all()
        DEBUG("All items on canvas: {}", all_items)
        for item_id in all_items:
            item_type = self.canvas.type(item_id)
            if item_type in ["rectangle", "text"]:
                self.canvas.delete(item_id)
                DEBUG("Deleted item ID {} of type {}", item_id, item_type)


    def draw_labels_on_canvas(self, labels):
        """Draw label bounding boxes on canvas with resize handles"""
        # Clear all previous label-related items
        # Clear all previous label-related items

              
        self.canvas.delete("label_box")
        self.canvas.delete("label_box_selected")
        self.canvas.delete("label_box_dragging")
        self.canvas.delete("label_box_resizing")
        self.canvas.delete("label_text")
        self.canvas.delete("resize_handle")
    

        

        # Remove any remaining items
        for item in self.canvas.find_withtag("label_box"):
            self.canvas.delete(item)
        for item in self.canvas.find_withtag("label_box_selected"):
            self.canvas.delete(item)
        for item in self.canvas.find_withtag("label_box_dragging"):
            self.canvas.delete(item)
        for item in self.canvas.find_withtag("label_box_resizing"):
            self.canvas.delete(item)
        for item in self.canvas.find_withtag("resize_handle"):
            self.canvas.delete(item)
        
        if not labels:
            DEBUG("No labels to draw")
            return
        
        # Update canvas size before drawing
        self.get_canvas_size()
        DEBUG("Drawing {} labels on canvas with size {}x{}", len(labels), self.canvas_width, self.canvas_height)
        
        # Define colors for different classes
        colors = [
            "#FF0000",  # Red
            "#00FF00",  # Green  
            "#0000FF",  # Blue
            "#FFFF00",  # Yellow
            "#FF00FF",  # Magenta
            "#00FFFF",  # Cyan
            "#FFA500",  # Orange
            "#800080",  # Purple
        ]
        
        for label in labels:
            # Convert label coordinates to canvas pixel coordinates
            x1, y1, x2, y2 = label_display_utils.convert_label_to_canvas_coords(
                label, self.canvas_width, self.canvas_height
            )
            
            # Determine color and style based on state
            if self.bbox_controller and self.bbox_controller.is_resizing and label == self.bbox_controller.resizing_label:
                # Resizing: special style with dotted line and bright color
                color = "#C00CC0"  # Purple for resizing
                width = 3
                tags = ("label_box", "label_box_resizing")
                dash = (3, 3)  # Dotted line pattern for resizing
            elif self.bbox_controller and self.bbox_controller.is_dragging and label == self.bbox_controller.dragging_label:
                # Dragging: special style with dashed line and bright color
                color = "#0CC0C0"  # Cyan for dragging
                width = 3
                tags = ("label_box", "label_box_dragging")
                dash = (5, 5)  # Dashed line pattern
            elif hasattr(label, 'selected') and label.selected:
                # Selected: red color with thicker border
                color = "#C00C0C"  # Red
                width = 3
                tags = ("label_box", "label_box_selected")
                dash = None
            else:
                # Not selected: green color
                color = "#0CC00C"
                width = 3
                tags = ("label_box",)
                dash = None
            
            # Draw bounding box
            rect_kwargs = {
                "outline": color,
                "width": width,
                "tags": tags
            }
            if dash:
                rect_kwargs["dash"] = dash
                
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                **rect_kwargs
            )
            
            # Draw resize handles for selected labels
            if hasattr(label, 'selected') and label.selected and self.bbox_controller:
                self.draw_resize_handles(label, x1, y1, x2, y2, color)
            
            # Draw class ID text
            text_x = x1
            text_y = y1 - 5 if y1 > 15 else y2 + 5

            # self.canvas.create_text(
            #     text_x, text_y,
            #     # text=str(label.class_id),
            #     text=wlm.get_label(label.class_id),
            #     fill=color,
            #     anchor="nw",

            #     tags="label_text"
            # )
            font_size = self.LABEL_FONT_SIZE
            draw_outlined_text(
                self.canvas,
                text_x, text_y,
                text=wlm.get_label(label.class_id),
                font=("Arial", font_size, "bold"),
                outline_color="white", fill_color="black", thickness=2, tags="label_text")

            DEBUG("Drew label: class_id={}, coords=({:.1f},{:.1f},{:.1f},{:.1f})",
                  label.class_id, x1, y1, x2, y2)


    def draw_resize_handles(self, label, x1, y1, x2, y2, color):
        """
        繪製 resize handle (右下角)
        
        Args:
            label (LabelObject): 標籤對象
            x1, y1, x2, y2 (float): bounding box 的 canvas 座標
            color (str): 邊框顏色
        """
        handle_size = self.bbox_controller.handle_size if self.bbox_controller else 10
        
        # 只繪製右下角 handle
        self.canvas.create_rectangle(
            x2 - handle_size,
            y2 - handle_size,
            x2,
            y2,
            fill="gray",
            tags="resize_handle"
        )
        
        DEBUG("Drew resize handle for label: class_id={}", label.class_id)

# Update text and index labels
    def update_text_box(self, content):
        if not self.SHOW_TEXT_BOX or self.text_box is None:
            DEBUG("Text box is not shown or not initialized.")
            return

        self.text_box.unbind("<<Modified>>")

        if not self.SHOW_TEXT_BOX:
            DEBUG("Text box is not shown as per configuration.")
            return
        self.text_box.config(state = "normal")
        self.text_box.delete("1.0", tk.END) # Clear the text box
        self.text_box.insert(tk.END, content)

        self.text_box.edit_modified(False)
        self.text_box.bind("<<Modified>>", self.on_text_modified)

    def update_index_label(self, index, path):
        DEBUG("update_index_label")
        self.index_label.config(text = f"{index + 1} : {len(path)}")
        DEBUG("Index label updated with index: {}", index)

    def highlight_yolo_line_for_label(self, selected_label):
        if not self.text_box:
            ERROR("Text box is not initialized.")
            return

        DEBUG("Highlighting YOLO line for label: {}", selected_label)
        self.text_box.tag_remove("highlight", "1.0", tk.END)  # Clear previous highlights

        if not selected_label or not hasattr(selected_label, 'line_index'):
            ERROR("No valid label selected.")
            return
        
        line_index = selected_label.line_index
        DEBUG("Highlighting line_index {}", line_index)
        start = f"{line_index + 1}.0"
        end = f"{line_index + 1}.end"
        self.text_box.tag_add("highlight", start, end)
        self.text_box.tag_config("highlight", background="#0C0CC0", foreground="#F0EF43", font = ("Segoe UI", 11, "bold"))

    def force_uppercase(self, event):
        current = self.input_box.get()
        upper = current.upper()
        if current != upper:
            self.input_box.delete(0, tk.END)
            self.input_box.insert(0, upper)
        self.input_box.config(fg = "#2D2D2D")

    def input_enter(self, event):
        """Handle Enter key press in input box"""
        DEBUG("input_enter triggered")
        if self.dispatch:
            input_text = self.input_box.get().strip()
            if input_text:
                DEBUG("Input text: {}", input_text)
                self.dispatch(UIEvent.INPUT_ENTER, {"text": input_text})
            else:
                ERROR("Input box is empty!")
        else:
            ERROR("Dispatch is not set!")

    def clear_input_box(self):
        """Clear the input box"""
        if self.input_box:
            self.input_box.delete(0, tk.END)
            DEBUG("Input box cleared")

    def focus_input_box(self):
        """Focus the input box"""
        if self.input_box:
            self.input_box.focus_set()
            DEBUG("Input box focused")

    def _on_input_focus_in(self, event):
        if self.input_box.get() == "請輸入車牌號碼":
            self.input_box.delete(0, tk.END)
            self.input_box.config(fg = "#8E8E79")

    def _on_input_focus_out(self, event):
        if not self.input_box.get():
            self.input_box.insert(0, "請輸入車牌號碼")
            self.input_box.config(fg = "#8E8E79")



# Button events
    def show_info_menu(self):
        # 取得按鈕在畫面中的位置
        x = self.info_button.winfo_rootx()
        y = self.info_button.winfo_rooty() + self.info_button.winfo_height()
        self.info_menu.tk_popup(x, y)
        
    def on_bt_click_reselect(self):
        DEBUG("on_bt_click_reselect")
        if self.dispatch:
            self.dispatch(UIEvent.RESELECT_BT_CLICK, {})

    def on_bt_click_crop(self):
        DEBUG("on_bt_click_crop")
        if self.dispatch:
            self.dispatch(UIEvent.CROP_BT_CLICK, {})

    def on_bt_click_add(self):
        DEBUG("on_bt_click_add")
        if self.dispatch:
            self.dispatch(UIEvent.ADD_BT_CLICK, {})        

    # Mouse events
    def on_mouse_click_right(self, event):
        DEBUG("on_mouse_click_right at ({}, {})", event.x, event.y)
        if self.dispatch:
            self.dispatch(UIEvent.MOUSE_RIGHT_CLICK, {"value": event})

    def on_mouse_press(self, event):
        """Handle mouse press event - support drawing, dragging, and resizing modes"""
        DEBUG("on_mouse_press at ({}, {})", event.x, event.y)
        
        if self.bbox_controller and self.bbox_controller.is_in_drawing_mode():
            # Drawing mode: start drawing
            if self.bbox_controller.start_drawing(event.x, event.y):
                if self.dispatch:
                    self.dispatch(UIEvent.MOUSE_LEFT_PRESS, {"value": event})
                return
        
        # Normal mode: handle selection, dragging, and resizing
        if self.dispatch:
            # Add operation type information for Controller
            self.dispatch(UIEvent.MOUSE_LEFT_PRESS, {
                "value": event, 
                "x": event.x, 
                "y": event.y,
                "supports_resize": True  # 標記支援 resize 功能
            })
    
    def on_mouse_release(self, event):
        """Handle mouse release event - support drawing, dragging, and resizing modes"""
        DEBUG("on_mouse_release at ({}, {})", event.x, event.y)
        
        if self.bbox_controller and self.bbox_controller.is_in_drawing_mode():
            # Drawing mode: complete drawing
            drawing_result = self.bbox_controller.finish_drawing(event.x, event.y)
            if drawing_result and self.dispatch:
                class_id = 0
                if hasattr(self, "class_id_vars") and self.class_id_vars:
                    selected = self.class_id_vars.get()
                    cid = wlm.get_class_id(selected)
                    if cid is not None:
                        class_id = cid
                self.dispatch(UIEvent.MOUSE_LEFT_RELEASE, {"value": event, "drawing_result": drawing_result, "class_id": class_id})
        elif self.bbox_controller and self.bbox_controller.is_resizing:
            # Resizing mode: complete resizing
            resized_label = self.bbox_controller.finish_resize()
            if resized_label and self.dispatch:
                self.dispatch(UIEvent.MOUSE_LEFT_RELEASE, {"value": event, "resized_label": resized_label})
        elif self.bbox_controller and self.bbox_controller.is_dragging:
            # Dragging mode: complete dragging
            dragged_label = self.bbox_controller.finish_drag()
            if dragged_label and self.dispatch:
                self.dispatch(UIEvent.MOUSE_LEFT_RELEASE, {"value": event, "dragged_label": dragged_label})
        
    def on_mouse_drag(self, event):
        """Handle mouse drag event - drawing preview, dragging, and resizing"""
        if self.bbox_controller and self.bbox_controller.is_in_drawing_mode():
            # Drawing mode: update preview
            self.bbox_controller.update_preview(event.x, event.y)
            if self.dispatch:
                self.dispatch(UIEvent.MOUSE_DRAG, {"value": event})
        elif self.bbox_controller and self.bbox_controller.is_resizing:
            # Resizing mode: update resize position
            self.bbox_controller.update_resize(event.x, event.y)
            if self.dispatch:
                self.dispatch(UIEvent.MOUSE_DRAG, {"value": event, "x": event.x, "y": event.y, "operation": "resize"})
        elif self.bbox_controller and self.bbox_controller.is_dragging:
            # Dragging mode: update drag position
            self.bbox_controller.update_drag(event.x, event.y)
            if self.dispatch:
                self.dispatch(UIEvent.MOUSE_DRAG, {"value": event, "x": event.x, "y": event.y, "operation": "drag"})

    # Key events
    def on_lc_press_switch_pen(self, event):
        """Left Ctrl key toggle drawing mode"""
        DEBUG("on_lc_press_switch_pen triggered")
        
        # Toggle drawing mode
        if self.bbox_controller:
            self.drawing_mode = self.bbox_controller.toggle_drawing_mode()
            DEBUG("Drawing mode toggled to: {}", self.drawing_mode)
            
            # Update status display
            self.update_drawing_mode_display()
        else:
            ERROR("bbox_controller is None!")
        
        if self.dispatch:
            self.dispatch(UIEvent.DRAWING_MODE_TOGGLE, {"value": event, "drawing_mode": self.drawing_mode})

    def on_rc_press(self, event):
        DEBUG("on_rc_press")

        if self.bbox_controller:
            self.bbox_controller.set_drawing_mode(True)
            self.update_drawing_mode_display()
        else:
            ERROR("bbox_controller is None!")

        if self.dispatch:
            self.drawing_mode = True
            self.dispatch(UIEvent.RIGHT_CTRL_PRESS, {"value": event, "drawing_mode": self.drawing_mode})

    def on_rc_release(self, event):
        DEBUG("on_rc_release")

        if self.bbox_controller:
            self.bbox_controller.set_drawing_mode(False)
            self.update_drawing_mode_display()
        else:
            ERROR("bbox_controller is None!")

        if self.dispatch:
            self.drawing_mode = False
            self.dispatch(UIEvent.RIGHT_CTRL_RELEASE, {"value": event, "drawing_mode": self.drawing_mode})

    def on_win_configure(self, event):
        """Handle window resize or move event"""
        # print("on_win_configure triggered")
        if self.dispatch:
            self.dispatch(UIEvent.WINDOW_POSITION, {})

    def on_delete_key(self, event):
        DEBUG("on_delete_key")
        if self.dispatch:
            self.dispatch(UIEvent.DELETE_KEY, {"value": event})

    def on_delete_image_button(self):
        DEBUG("on_delete_image_button")
        if self.dispatch:
            self.dispatch(UIEvent.DELETE_IMAGE,  None)
            
    def on_move_image_button(self):
        DEBUG("on_move_image_button")
        if self.dispatch:
            self.dispatch(UIEvent.MOVE_IMAGE,  None)

    def on_configuration_click(self):
        """Handle configuration button click"""
        DEBUG("on_configuration_click")
        if self.dispatch:
            self.dispatch(UIEvent.CONFIGURATION_BT_CLICK, None)

    def on_text_modified(self, event):
        if self.text_box.edit_modified():
            self.text_box.edit_modified(False)
            if self.dispatch:
                self.dispatch(UIEvent.TEXT_MODIFIED, {})
    
    def show_settings_dialog(self, current_settings, on_confirm_callback):
        """Show settings dialog"""
        try:
            DEBUG("Opening settings dialog")
            dialog = SettingsDialog(self.window, current_settings, on_confirm_callback)
            dialog.show()
        except Exception as e:
            ERROR("Error showing settings dialog: {}", e)
    
    def apply_ui_settings(self, settings):
        """Apply UI settings to show/hide components"""
        try:
            DEBUG("Applying UI settings: {}", settings)
            
            # Update internal settings
            self.SHOW_CLASS_ID_BUTTONS = settings.get('show_class_id_buttons', False)
            self.SHOW_TEXT_BOX = settings.get('show_text_box', True)
            self.SHOW_PREVIEW = settings.get('show_preview', True)
            self.SHOW_INPUT_BOX = settings.get('show_input_box', True)
            self.LABEL_FONT_SIZE = settings.get('label_font_size', 12)

            # Apply input box visibility (should be first, like in original creation)
            self.toggle_input_box(self.SHOW_INPUT_BOX)
            
            # Apply text box visibility (should be second, like in original creation)
            self.toggle_text_box(self.SHOW_TEXT_BOX)
            
            # Apply class ID buttons visibility
            self.toggle_class_id_buttons(self.SHOW_CLASS_ID_BUTTONS)
            
            # Apply preview panel visibility
            self.toggle_preview(self.SHOW_PREVIEW)
            
            DEBUG("UI settings applied successfully")
            
        except Exception as e:
            ERROR("Error applying UI settings: {}", e)
    
    def toggle_class_id_buttons(self, show):
        """Toggle class ID buttons panel visibility"""
        try:
            if show:
                # If we want to show but frame doesn't exist, create it
                if not hasattr(self, 'class_id_frame') or self.class_id_frame is None:
                    DEBUG("Creating class ID frame for show operation")
                    # Import here to avoid circular import issues
                    import config_utils

                    current_var = config_utils.get_class_id_vars()
                    labels = wlm.get_labels()
                    
                    # Create the frame
                    self.class_id_frame = tk.Frame(self.middle_frame, bg="#f8f8f8")
                    
                    # Create the buttons
                    self.class_id_vars = tk.StringVar(value=current_var or "0")
                    for i, label in enumerate(labels):
                        column = i // 13
                        row = i % 13
                        button = tk.Radiobutton(
                            self.class_id_frame, bg="#f8f8f8", font=("Segoe UI Mono", 10),
                            text=label, variable=self.class_id_vars, value=label, width=3, anchor="center", indicatoron=True,
                            command=lambda l=label: self.dispatch(UIEvent.CLASS_ID_CHANGE, {"label": l}) if self.dispatch else None
                        )
                        button.grid(row=row, column=column, padx=5, pady=5)
                
                # Show the frame
                try:
                    # Check if already packed by trying to get pack_info
                    self.class_id_frame.pack_info()
                except tk.TclError:
                    # Not packed, so pack it
                    self.class_id_frame.pack(side="right", fill="y")
                    DEBUG("Class ID buttons shown")
            else:
                # Hide the frame if it exists
                if hasattr(self, 'class_id_frame') and self.class_id_frame:
                    try:
                        # Check if packed by trying to get pack_info
                        self.class_id_frame.pack_info()
                        # If we get here, it's packed, so forget it
                        self.class_id_frame.pack_forget()
                        DEBUG("Class ID buttons hidden")
                    except tk.TclError:
                        # Already not packed
                        pass
        except Exception as e:
            ERROR("Error toggling class ID buttons: {}", e)
    
    def toggle_text_box(self, show):
        """Toggle text box visibility"""
        try:
            if show:
                # If we want to show but text_box doesn't exist, create it
                if not hasattr(self, 'text_box') or self.text_box is None:
                    DEBUG("Creating text box for show operation")
                    if hasattr(self, 'text_frame'):
                        self.text_box = tk.Text(
                            self.text_frame,
                            height=15, bg="white",
                            font=("Segoe UI", 11), fg="#8E8E79",
                            relief="sunken",
                            wrap="word"
                        )
                        self.text_box.tag_configure("left", justify="left")
                
                # Show the text box
                if hasattr(self, 'text_box') and self.text_box:
                    try:
                        # Check if already packed by trying to get pack_info
                        self.text_box.pack_info()
                    except tk.TclError:
                        # Not packed, so pack it
                        self.text_box.pack(side="top", fill="x", padx=20, pady=10)
                        DEBUG("Text box shown")
            else:
                # Hide the text box if it exists
                if hasattr(self, 'text_box') and self.text_box:
                    try:
                        # Check if packed by trying to get pack_info
                        self.text_box.pack_info()
                        # If we get here, it's packed, so forget it
                        self.text_box.pack_forget()
                        DEBUG("Text box hidden")
                    except tk.TclError:
                        # Already not packed
                        pass
        except Exception as e:
            ERROR("Error toggling text box: {}", e)
    
    def toggle_preview(self, show=None):
        """Toggle preview panel visibility"""
        try:
            if show is not None:
                self.SHOW_PREVIEW = show
            else:
                self.SHOW_PREVIEW = not self.SHOW_PREVIEW
                
            if hasattr(self, 'preview_frame'):
                if self.SHOW_PREVIEW:
                    try:
                        # Check if already packed by trying to get pack_info
                        self.preview_frame.pack_info()
                    except tk.TclError:
                        # Not packed, so pack it
                        self.preview_frame.pack(side="bottom", fill="both", expand=True)
                        DEBUG("Preview panel shown")
                        # Update preview if original image is available
                        if self.original_image is not None:
                            self.update_preview(self.original_image)
                else:
                    try:
                        # Check if packed by trying to get pack_info
                        self.preview_frame.pack_info()
                        # If we get here, it's packed, so forget it
                        self.preview_frame.pack_forget()
                        DEBUG("Preview panel hidden")
                    except tk.TclError:
                        # Already not packed
                        pass
            else:
                # If preview_frame doesn't exist yet but we want to show it, may need to trigger creation
                if show:
                    DEBUG("Preview frame not found, but show=True. May need to trigger creation first.")
        except Exception as e:
            ERROR("Error toggling preview: {}", e)
    
    def toggle_input_box(self, show):
        """Toggle input box visibility"""
        try:
            if show:
                # If we want to show but input_box doesn't exist, create it
                if not hasattr(self, 'input_box') or self.input_box is None:
                    DEBUG("Creating input box for show operation")
                    if hasattr(self, 'text_frame'):
                        self.input_box = tk.Entry(self.text_frame, font=("Segoe UI", 11), fg="#424242")
                        self.input_box.insert(0, "請輸入車牌號碼")
                        self.input_box.bind("<FocusIn>", self._on_input_focus_in)
                        self.input_box.bind("<FocusOut>", self._on_input_focus_out)
                        self.input_box.bind("<Return>", self.input_enter)
                        self.input_box.bind("<KeyRelease>", self.force_uppercase)
                
                # Show the input box
                if hasattr(self, 'input_box') and self.input_box:
                    try:
                        # Check if already packed by trying to get pack_info
                        self.input_box.pack_info()
                    except tk.TclError:
                        # Not packed, so pack it
                        self.input_box.pack(side="top", fill="x", padx=20, pady=10)
                        DEBUG("Input box shown")
            else:
                # Hide the input box if it exists
                if hasattr(self, 'input_box') and self.input_box:
                    try:
                        # Check if packed by trying to get pack_info
                        self.input_box.pack_info()
                        # If we get here, it's packed, so forget it
                        self.input_box.pack_forget()
                        DEBUG("Input box hidden")
                    except tk.TclError:
                        # Already not packed
                        pass
        except Exception as e:
            ERROR("Error toggling input box: {}", e)

    def next_image(self, event):
        DEBUG("next_image")
        if self.dispatch:
            self.dispatch(UIEvent.RIGHT_PRESS, {"value": event})

    def previous_image(self, event):
        DEBUG("previous_image")
        if self.dispatch:
            self.dispatch(UIEvent.LEFT_PRESS, {"value": event})

    # Bind key and mouse with events
    def setup_events(self):
        self.window.bind("<Left>", self.previous_image)
        self.window.bind("<Right>", self.next_image)

        # Ctrl key event binding
        self.window.bind("<Control_L>", self.on_lc_press_switch_pen)

        self.window.bind("<Control_R>", self.on_rc_press)
        self.window.bind("<KeyRelease-Control_R>", self.on_rc_release)

        #Windows changes posiotion or size
        self.window.bind("<Configure>", self.on_win_configure)

        # Delete key event binding
        self.window.bind("<Delete>", self.on_delete_key)

        # Mouse event binding (support drawing functionality)
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Button-3>", self.on_mouse_click_right)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def select_folder(self, title):
        folder_path = filedialog.askdirectory(parent = self.window, title = title)
        return folder_path

    def show_error(self, msg):
        messagebox.showerror("Error", str(msg))

    def create_context_menu(self):
        """創建右鍵選單"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="刪除", command=self.delete_from_context_menu)
    
    def show_context_menu(self, event):
        """顯示右鍵菜單"""
        try:
            # Show context menu at cursor position
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def delete_from_context_menu(self):
        """從右鍵菜單觸發刪除"""
        # 顯示確認對話框
        result = messagebox.askyesno("Delete", "Delete selected box?")
        if result and self.dispatch:
            self.dispatch(UIEvent.DELETE_KEY, {"value": None})
    
    def cancel_current_drawing(self):
        """Cancel current drawing"""
        if self.bbox_controller:
            self.bbox_controller.cancel_drawing()
    
    def update_drawing_mode_display(self):
        """Update drawing mode status display"""
        if self.drawing_mode and self.bbox_controller.is_in_drawing_mode():
            self.drawing_mode_label.config(text="繪框模式", fg="#C00CC0")
        else:
            self.drawing_mode_label.config(text="普通模式", fg="#8E8E79")
    
    def update_selection_status_display(self, selected_label=None):
        """Update selection status display"""
        if self.bbox_controller and self.bbox_controller.is_dragging:
            # 拖曳模式顯示
            dragging_label = self.bbox_controller.dragging_label
            status_text = f"拖曳中：class_id={dragging_label.class_id}"
            self.selection_status_label.config(text=status_text, fg="#0CC0C0")
        elif selected_label:
            status_text = f"已選中：class_id={selected_label.class_id}"
            self.selection_status_label.config(text=status_text, fg="#C00C0C")
        else:
            self.selection_status_label.config(text="未選中任何框", fg="#8E8E79")
    
    def update_dragging_status_display(self, is_dragging=False, dragged_label=None):
        """
        更新拖曳狀態顯示
        
        Args:
            is_dragging (bool): 是否正在拖曳
            dragged_label (LabelObject): 被拖曳的標籤對象
        """
        if is_dragging and dragged_label:
            status_text = f"拖曳中：class_id={dragged_label.class_id}, 座標=({dragged_label.cx_ratio:.3f}, {dragged_label.cy_ratio:.3f})"
            self.selection_status_label.config(text=status_text, fg="#0CC0C0")
        else:
            # Restore selection status display
            self.update_selection_status_display(self.bbox_controller.get_selected_label() if self.bbox_controller else None)
    
    def update_sorting_status(self, label_count=0, plate_count=0):
        """
        更新狀態以顯示標籤已排序
        
        Args:
            label_count (int): 排序的標籤數量
            plate_count (int): 偵測到的車牌數量
        """
        if label_count > 0:
            status_text = f"標籤已自動排序：{label_count} 個標籤，{plate_count} 個車牌"
            self.selection_status_label.config(text=status_text, fg="#C0C00C")
            # 3秒後恢復正常狀態顯示
            self.window.after(3000, lambda: self.update_selection_status_display())

    def run(self):
        if self.dispatch:
            self.window.after_idle(lambda: self.dispatch(UIEvent.WINDOW_READY, {}))
        self.window.mainloop()


# for implementation testing
if __name__ == "__main__":
    ui = UI()
    ui.run()
