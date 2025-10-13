from cProfile import label
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
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
from constants import CLASS_ID_COLOR_MAP
from tkinter import ttk
from DragableVerticalLine import DraggableVerticalLine
from collections import deque

DEFAULT_W = 1920
DEFAULT_H = 1080
DEFAULT_MIN_PLATE_WIDTH    = 70
class UI:
    def __init__(self):
        self.dispatch = None
        width, height = config_utils.get_window_size()
        DEBUG(f"Window size from config: {width}x{height}")
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
        self.current_labels = []  # Store current labels for cursor updates
        
        # Initialize options
        self.original_image = None
        self._ctx = None

        # Load UI settings from config
        self.SHOW_CLASS_ID_BUTTONS = config_utils.get_show_class_id_buttons()
        self.SHOW_TEXT_BOX = config_utils.get_show_text_box()
        self.SHOW_PREVIEW = config_utils.get_show_preview()
        self.SHOW_INPUT_BOX = config_utils.get_show_input_box()
        self.SHOW_CLASSIFY_FRAME= config_utils.get_show_classify_frame()
        self.SHOW_CUT_IMAGE = config_utils.get_show_cut_image()
        self.SHOW_BBOX_DIMENSIONS = config_utils.get_show_bbox_dimensions()
        self.SHOW_TILT_ANGLE = config_utils.get_show_tilt_angle()
        self.MIN_BBOX_WIDTH_THRESHOLD = config_utils.get_min_bbox_width_threshold()
        self.LABEL_FONT_SIZE = config_utils.get_ui_label_font_size_in_config()
        self.PROPORTIONAL_SCALING = config_utils.get_proportional_scaling()

        # Initialize plate memory
        self.recent_plates = deque(maxlen=5)
        self.plate_memory_frame = None
        self.plate_memory_buttons = []

        # Load existing plate memory from config
        self.load_plate_memory_from_config()

        self.setup_ui()
        self.setup_events()
       
    def set_dispatcher(self, event_dispatcher):
        self.dispatch = event_dispatcher
        
# Define UI components
    def setup_ui(self):
        self.create_top_area()
        self.create_middle_area()
        self.create_classification_area()
                
        self.create_cut_image_bt()
        self.create_bottom_area()

    def create_top_area(self):
        self.toolbar =  tk.Frame(self.window, bg = "#F4F4F4")
        self.toolbar.pack(side = "top", fill = "x")

        self.select_folders_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 16, height = 1,
            text = "Reselect Folders", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_bt_click_reselect
        )
        self.select_folders_button.pack(side = "left", padx = 5)
        
        self.crop_all_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 4, height = 1,
            text = "Crop", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_bt_click_crop
        )
        self.crop_all_button.pack(side = "left")

        self.delete_image_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 4, height = 1,
            text="Delete", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.delete_image)
        self.delete_image_button.pack(side = "left", padx = 5)
        
        self.move_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 8, height = 1,
            text="Move to", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.show_move_menu)
        self.move_button.pack(side = "left", padx = 5)
        
        # 建立 move to  menu
        self.move_menu = tk.Menu(self.window, tearoff=0)
        self.move_menu.add_command(label="special plates", command=self.move_to_special_plates)
        self.move_menu.add_command(label="uncertain", command=self.move_to_uncertain)
        
        self.batch_sort_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 10, height = 1,
            text = "Batch Sort", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_bt_click_batch_sort
        )
        self.batch_sort_button.pack(side = "left", padx = 5)

        self.scan_plates_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 10, height = 1,
            text = "Scan Plates", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_bt_click_scan_plates
        )
        self.scan_plates_button.pack(side = "left", padx = 5)

        self.settings_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 12, height = 1,
            text = "Configuration", fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.on_configuration_click
        )
        self.settings_button.pack(side = "left", padx = 5)

        self.show_info_button = tk.Button(
            self.toolbar, bg = "#F4F4F4",
            width = 4, height = 1,
            text="Info", font=("Segoe UI", 10), fg = "#0C0CC0",
            relief = "flat", bd = 2,
            command = self.show_info_dialog)
        self.show_info_button.pack(side = "left", padx =0)
        
        # Timer display label (shows countdown when active)
        self.timer_label = tk.Label(
            self.toolbar, bg = "#F4F4F4",
            text="", font=("Segoe UI", 11, "bold"), fg = "blue"
        )
        self.timer_label.pack(side = "left", padx = 10)


    def create_middle_area(self):
        self.middle_frame = tk.Frame(self.window)
        self.middle_frame.pack(side = "top", fill = "both", expand = True)

        self.create_canvas()
        
        # Initialize drawing controller
        self.bbox_controller = bbox_controller.BBoxController(self.canvas)
        
        # Set properties for reference box feature
        self.bbox_controller.show_bbox_dimensions = self.SHOW_BBOX_DIMENSIONS
        self.bbox_controller.min_width_threshold = self.MIN_BBOX_WIDTH_THRESHOLD
        
        # Get original image width for proper scaling
        original_height, original_width = config_utils.get_image_info()
        self.bbox_controller.original_image_width = original_width

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
        self.create_right_bottom_area()
    
    def create_right_bottom_area(self):
        self.right_bottom_frame = tk.Frame(self.bottom_frame, bg = "#FAFAFA")
        self.right_bottom_frame.pack(side = "right", expand = True, fill = "both")
        
        self.create_hint_area()
        self.create_preview_area()
            
  
    def create_classification_area(self):
        """Main function to create the classification area."""
        self.create_classification_frame()
        self.create_classify_cbts()
        self.create_submit_button()
        if self.SHOW_CLASSIFY_FRAME is False:
            self.classification_frame.pack_forget()

    def create_classification_frame(self):
        """Create the classification frame."""
        self.classification_frame = tk.Frame(self.window, relief = "ridge", bd = 2, bg = "#FAFAFA")
        # self.classification_frame.pack(side = "top", fill = "x")
        self.classification_frame.pack(side="top", anchor="center")
    
    def clear_all_classify_checkbuttons(self):
        for var in self.selected_plate_types.values():
            var.set(0)      
               
    def create_classify_cbts(self):
        """Create classify_cbts dynamically for each classification label."""
        from constants import classification_label_map
    
        # Dictionary to store the state of each Checkbutton
        # self.selected_plate_types = {label: tk.BooleanVar() for label in classification_labels}
        self.selected_plate_types = {key: tk.BooleanVar() for key in classification_label_map.values()}
        
        # self.classify_cbts = {}
        
        # Create classify_cbts dynamically for each label
        for index, (key, value) in enumerate(classification_label_map.items()):
            checkbutton = tk.Checkbutton(
                self.classification_frame,
                text=key,
                variable=self.selected_plate_types[value],
                onvalue=True,
                offvalue=False,
                bg="lightgray",
                fg="black",
                font=("Segoe UI", 12),  # Increased font size
                anchor="w"  # Align text to the left
            )
  
            
            checkbutton.grid(row=0, column=index, padx=5, pady=5)
        
           
            # Store the Checkbutton in the dictionary with the label as the key
            # self.classify_cbts[label] = checkbutton
            
            
    def create_submit_button(self):
        """Create the submit button."""
        from constants import classification_label_map

        def submit_callback():
            selected_types = [label for label, var in self.selected_plate_types.items() if var.get()]
            DEBUG(f"Selected plate types: {selected_types}")
            if not selected_types:
                INFO("No plate types selected for classification.")
                self.show_warning("classify types is not selected")
                return
            if self.dispatch:
                self.dispatch(UIEvent.MOVE_IMAGE_CLASSIFIED, {"plate_types": selected_types})

        self.submit_button = tk.Button(
            self.classification_frame,
            text="Submit",
            command=submit_callback,
            width=20,
            height=2,
            bg="green",
            fg="white",
            font=("Segoe UI", 12, "bold")
        )
   
        self.submit_button.grid(row=1, column=0, columnspan=len(classification_label_map), pady=10)         
  
    def create_cut_image_bt(self):
        """Create the cut image button and its functionality."""
        self.cut_frame = tk.Frame(self.window, relief = "ridge", bd = 2, bg = "#FAFAFA")
        self.cut_frame.pack(side="top", anchor="center")
        self.cut_image_button = tk.Button(
            self.cut_frame,
            text="CUT",
            font=("Segoe UI", 12),
            width=20,
            height=2,
            bg="green",
            fg="white",
            command=self.on_cut_image_button_click
        )
        self.cut_image_button.pack(side="left", padx=10, pady=10)
        
        if self.SHOW_CUT_IMAGE is False:
            self.cut_frame.pack_forget()
        
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

            # Initialize plate memory frame
            self.plate_memory_frame = tk.Frame(self.text_frame, bg="#FAFAFA")
            self.plate_memory_frame.pack(side="top", fill="x", padx=20, pady=(0, 10))

            # Update plate memory buttons on startup
            self.update_plate_memory_buttons()

        else:
            DEBUG("Input box is not shown as per configuration.")
            self.input_box = None
            self.plate_memory_frame = None

        # Initialize text box if enabled - using Notebook for tab switching
        if self.SHOW_TEXT_BOX:
            # Create Notebook (tab control)
            self.text_notebook = ttk.Notebook(self.text_frame)
            self.text_notebook.pack(side="top", fill="both", expand=True, padx=20, pady=10)

            # Tab 1: Labels (original text box)
            self.labels_tab = tk.Frame(self.text_notebook, bg="#FAFAFA")
            self.text_notebook.add(self.labels_tab, text="Labels")

            self.label_text_box = tk.Text(
                self.labels_tab,
                height=15, bg="#FAFAFA",
                font=("Segoe UI", 11), fg="#2d2d2d",
                relief="sunken",
                wrap="word"
            )
            self.label_text_box.tag_configure("left", justify="left")
            self.label_text_box.pack(fill="both", expand=True)
            self.label_text_box.bind("<<Modified>>", self.on_text_modified)

            # Tab 2: Console (for scan results)
            self.console_tab = tk.Frame(self.text_notebook, bg="#FAFAFA")
            self.text_notebook.add(self.console_tab, text="Console")

            self.console_text_box = tk.Text(
                self.console_tab,
                height=15, bg="#2d2d2d",
                font=("Consolas", 10), fg="#00ff00",
                relief="sunken",
                wrap="none",
                state="disabled"  # Read-only
            )
            self.console_text_box.pack(fill="both", expand=True)

        else:
            DEBUG("Text box is not shown as per configuration.")
            self.label_text_box = None
            self.console_text_box = None
            self.text_notebook = None

        self.path_label = tk.Label(self.text_frame, bg = "#FAFAFA", font = ("Segoe UI", 11), fg = "#C0C00C", anchor = "w", justify = "left", wraplength = 700)
        self.path_label.bind("<Button-1>", self._on_copy_file_name_text)
        self.path_label.pack(side = "bottom", fill = "x", padx = 20, pady = 10)

    def create_hint_area(self):
        self.hint_frame = tk.Frame(self.right_bottom_frame, bg = "#FAFAFA")
        self.hint_frame.pack(side = "top", expand = True, fill = "x")

        # Create container frame for page number display
        self.index_frame = tk.Frame(self.hint_frame, bg = "#FAFAFA")
        self.index_frame.grid(row = 0, column = 2, sticky = "nwse")

        # Button to jump to first page
        self.jump_first_button = tk.Button(
            self.index_frame,
            text = "⏮",
            bg = "#FAFAFA",
            fg = "#C0C00C",
            font = ("Segoe UI", 14),
            relief = "solid",
            bd = 0,
            padx = 3,
            pady = 1,
            cursor = "hand2",
            command = lambda: self.dispatch(UIEvent.JUMP_TO_FIRST, {}) if self.dispatch else None
        )
        self.jump_first_button.pack(side = "left", padx = (0, 3))

        # Entry for current page number (editable)
        self.index_entry = tk.Entry(
            self.index_frame,
            bg = "#FAFAFA",
            fg = "#C0C00C",
            font = ("Segoe UI", 11),
            width = 5,
            justify = "right",
            relief = "solid",
            bd = 0,
            highlightthickness = 1,
            highlightcolor = "#C0C00C",
            highlightbackground = "#D0D0D0"
        )
        self.index_entry.pack(side = "left")
        self.index_entry.bind("<Return>", lambda e: self.on_index_entry_enter())

        # Label for total pages (read-only)
        self.index_total_label = tk.Label(self.index_frame, bg = "#FAFAFA", fg = "#C0C00C", font = ("Segoe UI", 11), text = "/0")
        self.index_total_label.pack(side = "left")

        # Button to jump to last page
        self.jump_last_button = tk.Button(
            self.index_frame,
            text = "⏭",
            bg = "#FAFAFA",
            fg = "#C0C00C",
            font = ("Segoe UI", 14),
            relief = "solid",
            bd = 0,
            padx = 3,
            pady = 1,
            cursor = "hand2",
            command = lambda: self.dispatch(UIEvent.JUMP_TO_LAST, {}) if self.dispatch else None
        )
        self.jump_last_button.pack(side = "left", padx = (3, 0))

        self.total_pages = 0  # Store total pages for validation


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
        self.selection_status_label.grid(row = 0, column = 1, sticky = "nw", padx = (20, 20))
        
        # Add quick correct button
        self.quick_correct_button = tk.Button(
            self.hint_frame, bg = "#E0E0E0", text = "快速校正車牌字元(熱鍵: T)",
            fg = "#2D2D2D", font = ("Segoe UI", 10),
            command = lambda: self.dispatch(UIEvent.QUICK_CORRECT, {}) if self.dispatch else None
        )
        self.quick_correct_button.grid(row = 0, column = 3, sticky = "w", padx = (10, 0))

        # Add tilt angle display label
        self.tilt_angle_label = tk.Label(
            self.hint_frame, bg = "#FAFAFA", text = "N/A",
            fg = "#8E8E79", font = ("Segoe UI", 11)
        )
        self.tilt_angle_label.grid(row = 0, column = 4, sticky = "w", padx = (10, 0))

        # Add IoU display label
        self.iou_label = tk.Label(
            self.hint_frame, bg = "#FAFAFA", text = "IoU: N/A",
            fg = "#8E8E79", font = ("Segoe UI", 11)
        )
        self.iou_label.grid(row = 0, column = 5, sticky = "w", padx = (10, 0))

    def create_preview_area(self):
        if not self.SHOW_PREVIEW:
            DEBUG("Preview area is not shown as per configuration.")
            return
            
        # Create preview frame with border
        self.preview_frame = tk.Frame(self.right_bottom_frame, bg = "#FAFAFA", relief = "ridge", bd = 2)
        self.preview_frame.pack(side = "top", fill = "both", expand = True)

        # Left: Crop
        self.crop_container = tk.Frame(self.preview_frame, bg="#FAFAFA", relief="ridge", bd=2)
        self.crop_container.pack(side = "left", fill = "both", expand = True)
        tk.Label(self.crop_container, text="Crop", bg="#FAFAFA", fg="#2d2d2d",
                font=("Segoe UI", 11, "bold")).pack(side="top", pady=5)

        # Create zoom scale buttons toolbar
        zoom_toolbar = tk.Frame(self.crop_container, bg="#FAFAFA")
        zoom_toolbar.pack(side="top", pady=(0, 5))

        tk.Label(zoom_toolbar, text="縮放:", bg="#FAFAFA", fg="#666666",
                font=("Segoe UI", 9, "bold")).pack(side="left", padx=(8, 5))

        # Store zoom buttons for state management
        self.preview_zoom_buttons = {}
        zoom_scales = [1.0, 1.5, 2.0, 3.0, 3.5]
        zoom_labels = ["x1", "x1.5", "x2", "x3", "x3.5"]

        for scale, label in zip(zoom_scales, zoom_labels):
            btn = tk.Button(
                zoom_toolbar,
                text=label,
                width=5,
                font=("Segoe UI", 9),
                relief="flat",
                bg="#F5F5F5",
                fg="#555555",
                activebackground="#E8E8E8",
                activeforeground="#333333",
                bd=1,
                highlightthickness=0,
                cursor="hand2",
                command=lambda s=scale: self.on_preview_zoom_changed(s)
            )
            btn.pack(side="left", padx=2)
            self.preview_zoom_buttons[scale] = btn

            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E8E8E8") if b.cget("relief") == "flat" else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#F5F5F5") if b.cget("relief") == "flat" else None)

        self._create_canvas_with_scrollbars("crop", parent_override=self.crop_container)

        # Right: Original
        self.original_container = tk.Frame(self.preview_frame, bg="#FAFAFA", relief="ridge", bd=2)
        self.original_container.pack(side = "right", fill = "both", expand = True)
        tk.Label(self.original_container, text="原圖", bg="#FAFAFA", fg="#2d2d2d",
                font=("Segoe UI", 11, "bold")).pack(side="top", pady=5)
        self._create_canvas_with_scrollbars("original", parent_override=self.original_container)

        # Set minimum size for preview frame
        self.preview_frame.update_idletasks()
        self.preview_frame.configure(width=250, height=250)

        # Initialize preview state
        self.preview_image = None
        self.preview_photo_image = None
        self.original_image_for_preview = None
        self.original_photo_image = None
        self.pending_original_image = None
        self.original_image_labels = []  # List of LabelObject instances for original image

        # Initialize preview zoom scale
        self.preview_zoom_scale = config_utils.get_preview_zoom_scale()
        self._update_zoom_button_states()

        # Schedule placeholder text after window is rendered
        if self.preview_canvas:
            self.preview_canvas.after_idle(self._add_preview_placeholder)
        if self.original_canvas:
            self.original_canvas.after_idle(lambda: self._add_placeholder_to_canvas(self.original_canvas, "無原圖"))

        # Bind magnifier events to both canvases
        self._bind_canvas_events(self.preview_canvas, "crop")
        self._bind_canvas_events(self.original_canvas, "original")
        
        # Initialize magnifier state
        self.magnifier_tooltip = None
        self.is_dragging_preview = False
        self.is_dragging_original = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Initialize magnifier cache (LRU cache for magnified regions) 
        self.magnifier_cache = {}
        
        # Initialize preview magnifier drag state (separate from main canvas bbox selection)
        self.preview_magnifier_dragging = False
        self.preview_magnifier_drag_start_x = 0
        self.preview_magnifier_drag_start_y = 0
        self.preview_magnifier_selection_rect = None

        # Initialize preview click marker state (for showing clicked position on main canvas)
        self.preview_click_marker_lines = []
        self.preview_click_marker_visible = False
    
    def _create_canvas_with_scrollbars(self, canvas_type, parent_override=None):
        """Create a canvas with scrollbars for the specified type (crop or original)"""
        if parent_override is not None:
            parent_frame = parent_override
            if canvas_type == "crop":
                canvas_name = "preview_canvas"
                v_scrollbar_name = "preview_v_scrollbar"
                h_scrollbar_name = "preview_h_scrollbar"
                canvas_frame_name = "preview_canvas_frame"
            else:  # original
                canvas_name = "original_canvas"
                v_scrollbar_name = "original_v_scrollbar"
                h_scrollbar_name = "original_h_scrollbar"
                canvas_frame_name = "original_canvas_frame"

        else:
            if canvas_type == "crop":
                parent_frame = self.crop_container
                canvas_name = "preview_canvas"
                v_scrollbar_name = "preview_v_scrollbar"
                h_scrollbar_name = "preview_h_scrollbar"
                canvas_frame_name = "preview_canvas_frame"
            else:
                parent_frame = self.original_container
                canvas_name = "original_canvas"
                v_scrollbar_name = "original_v_scrollbar"
                h_scrollbar_name = "original_h_scrollbar"
                canvas_frame_name = "original_canvas_frame"
        
        # Create canvas container
        canvas_frame = tk.Frame(parent_frame, bg = "#FAFAFA")
        canvas_frame.pack(fill = "both", expand = True)
        setattr(self, canvas_frame_name, canvas_frame)
        
        # Create scrollbars
        v_scrollbar = tk.Scrollbar(canvas_frame, orient = "vertical")
        h_scrollbar = tk.Scrollbar(canvas_frame, orient = "horizontal")
        setattr(self, v_scrollbar_name, v_scrollbar)
        setattr(self, h_scrollbar_name, h_scrollbar)
        
        # Create canvas with dynamic size
        canvas = tk.Canvas(
            canvas_frame,
            bg = "white",
            highlightthickness = 1,
            highlightbackground = "#8E8E79",
            yscrollcommand = v_scrollbar.set,
            xscrollcommand = h_scrollbar.set
        )
        setattr(self, canvas_name, canvas)
        
        # Configure scrollbars
        v_scrollbar.config(command = canvas.yview)
        h_scrollbar.config(command = canvas.xview)
        
        # Pack canvas and scrollbars
        canvas.grid(row = 0, column = 0, sticky = "nsew")
        v_scrollbar.grid(row = 0, column = 1, sticky = "ns")
        h_scrollbar.grid(row = 1, column = 0, sticky = "ew")
        
        # Configure grid weights
        canvas_frame.grid_rowconfigure(0, weight = 1)
        canvas_frame.grid_columnconfigure(0, weight = 1)
    
    def _bind_canvas_events(self, canvas, canvas_type):
        """Bind events to the specified canvas"""
        if canvas:
            canvas.bind("<Enter>", lambda event: self.on_preview_enter(event, canvas_type))
            canvas.bind("<Leave>", lambda event: self.on_preview_leave(event, canvas_type))
            
            # Left mouse events for magnifier drag selection
            canvas.bind("<Button-1>", lambda event: self.on_preview_left_press(event, canvas_type))
            canvas.bind("<B1-Motion>", lambda event: self.on_preview_left_drag(event, canvas_type))
            canvas.bind("<ButtonRelease-1>", lambda event: self.on_preview_left_release(event, canvas_type))
            
            # Right mouse events for canvas dragging
            canvas.bind("<Button-3>", lambda event: self.on_preview_right_drag_start(event, canvas_type))
            canvas.bind("<B3-Motion>", lambda event: self.on_preview_right_drag(event, canvas_type))
            canvas.bind("<ButtonRelease-3>", lambda event: self.on_preview_right_drag_end(event, canvas_type))
        self.cache_access_order = []
        
        # Load magnifier configuration
        self.load_magnifier_config()
    
    
    
    def _add_preview_placeholder(self):
        """Add placeholder text to preview canvas after it has been rendered"""
        self._add_placeholder_to_canvas(self.preview_canvas, "尚未載入圖片")
    
    def _add_placeholder_to_canvas(self, canvas, text):
        """Add placeholder text to specified canvas after it has been rendered"""
        if not canvas:
            return
            
        # Get actual canvas dimensions
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # Add placeholder text at center
        canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text = text,
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

        try:
            if self.bbox_controller and self.original_image is not None:
                w, h = self.original_image.size
                self.bbox_controller.original_image_width = w
                self.bbox_controller.original_image_height = h
                DEBUG("bbox_controller.original_image_width set to {}", w)
                DEBUG("bbox_controller.original_image_height set to {}", h)
        except Exception as e:
            ERROR("Failed to update bbox_controller.original_image_width: {}", str(e))
    
    def set_original_image_for_preview(self, original_image_for_preview):
        """Set the original image for preview (right-bottom '原圖' panel).
        
        Args:
            original_image_for_preview: PIL.Image object of the original image for preview
        """
        self.original_image_for_preview = original_image_for_preview
        self.pending_original_image = original_image_for_preview
        
        if original_image_for_preview:
            DEBUG("Original image for preview set, will update when tab is selected")
            # Only update if original tab is currently selected
            try:
                if hasattr(self, 'original_canvas') and self.original_canvas:
                    self.update_original_preview(original_image_for_preview)
            except:
                pass  # Tab not ready yet, will update on tab change
        else:
            DEBUG("No original image for preview available")
            # Clear the original preview tab
            if hasattr(self, 'original_canvas') and self.original_canvas:
                self.clear_original_preview()

    def set_original_image_labels(self, original_image_labels):
        """Set the labels for original image preview
        
        Args:
            original_image_labels: List of LabelObject instances for original image
        """
        self.original_image_labels = original_image_labels if original_image_labels else []
        DEBUG("Set {} original image labels for preview", len(self.original_image_labels))

    def update_preview(self, original_image):
        """Update preview with the full original image

        Args:
            original_image: PIL Image object
        """
        if not self.SHOW_PREVIEW or self.preview_canvas is None:
            return

        from PIL import Image, ImageTk
        import image_utils

        # Clear magnifier cache when preview updates
        self.clear_magnifier_cache()

        # Clear previous preview
        self.preview_canvas.delete("all")

        # Get original image dimensions
        img_width, img_height = original_image.size

        # Apply zoom scale
        zoom_scale = getattr(self, 'preview_zoom_scale', 1.0)
        scaled_width = int(img_width * zoom_scale)
        scaled_height = int(img_height * zoom_scale)

        # Resize image if zoom scale is not 1.0
        if abs(zoom_scale - 1.0) > 0.01:
            scaled_image = image_utils.resize_image(original_image, (scaled_width, scaled_height))
            self.preview_photo_image = ImageTk.PhotoImage(scaled_image)
        else:
            # Use original size
            self.preview_photo_image = ImageTk.PhotoImage(original_image)

        # Display on preview canvas
        self.preview_canvas.create_image(0, 0, anchor = "nw", image = self.preview_photo_image, tags = "preview_image")

        # Update scroll region to match scaled image size
        self.preview_canvas.config(scrollregion = (0, 0, scaled_width, scaled_height))

        # Get canvas dimensions for info text positioning
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        # Add info text at visible position
        if abs(zoom_scale - 1.0) > 0.01:
            info_text = f"原始: {img_width}×{img_height} | 縮放: {zoom_scale}x ({scaled_width}×{scaled_height})"
        else:
            info_text = f"原始尺寸: {img_width}×{img_height}"
        self.preview_canvas.create_text(
            10, canvas_height - 5,
            text = info_text,
            fill = "#8E8E79",
            font = ("Segoe UI", 9),
            anchor = "sw",
            tags = ("info_text", "overlay")
        )

        DEBUG("Preview updated with {}x zoom: original {}×{} -> scaled {}×{}",
              zoom_scale, img_width, img_height, scaled_width, scaled_height)

    def _update_zoom_button_states(self):
        """Update zoom button visual states to show current selection"""
        if not hasattr(self, 'preview_zoom_buttons'):
            return

        for scale, btn in self.preview_zoom_buttons.items():
            if abs(scale - self.preview_zoom_scale) < 0.01:  # Float comparison tolerance
                # Selected state - darker blue with white text for better contrast
                btn.config(
                    relief="flat",
                    bg="#2E7BD4",
                    fg="#FFFFFF",
                    font=("Segoe UI", 9, "bold"),
                    bd=1,
                    highlightthickness=1,
                    highlightbackground="#2E7BD4"
                )
            else:
                # Unselected state - flat style with neutral color
                btn.config(
                    relief="flat",
                    bg="#F5F5F5",
                    fg="#555555",
                    font=("Segoe UI", 9),
                    bd=1,
                    highlightthickness=0
                )

    def on_preview_zoom_changed(self, scale):
        """Handle preview zoom scale button click

        Args:
            scale: New zoom scale factor (1.0, 1.5, 2.0, 3.0, 3.5)
        """
        DEBUG("Preview zoom scale changed to: {}x", scale)

        # Update zoom scale
        self.preview_zoom_scale = scale

        # Update button states
        self._update_zoom_button_states()

        # Save to config
        config_utils.save_preview_zoom_scale(scale)

        # Refresh preview display if image is loaded
        if self.original_image:
            self.update_preview(self.original_image)

        INFO("Preview zoom scale set to {}x", scale)

    def update_original_preview(self, original_image):
        """Update original preview tab with auto-scaled original image
        
        Args:
            original_image: PIL Image object
        """
        if not self.SHOW_PREVIEW or not hasattr(self, 'original_canvas') or self.original_canvas is None:
            return
            
        from PIL import Image, ImageTk
        import image_utils
        
        # Clear previous preview
        self.original_canvas.delete("all")
        
        # Get original image dimensions
        img_width, img_height = original_image.size
        
        # Get canvas dimensions
        self.original_canvas.update_idletasks()
        canvas_width = self.original_canvas.winfo_width()
        canvas_height = self.original_canvas.winfo_height()
        
        # Check if canvas has valid dimensions
        if canvas_width <= 0 or canvas_height <= 0:
            DEBUG("Canvas not ready for original preview: {}x{}", canvas_width, canvas_height)
            # Store image for later update when tab is selected
            self.pending_original_image = original_image
            return
        
        # Calculate scale to fit canvas while maintaining aspect ratio
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y)  # Use smaller scale to ensure image fits
        
        # Calculate scaled dimensions with minimum size protection
        scaled_width = max(1, int(img_width * scale))
        scaled_height = max(1, int(img_height * scale))
        
        # Resize image to fit canvas
        scaled_image = image_utils.resize_image(original_image, (scaled_width, scaled_height))
        self.original_photo_image = ImageTk.PhotoImage(scaled_image)
        
        # Center the scaled image on canvas
        x_offset = (canvas_width - scaled_width) // 2
        y_offset = (canvas_height - scaled_height) // 2
        
        # Display scaled image centered on canvas
        self.original_canvas.create_image(x_offset, y_offset, anchor = "nw", image = self.original_photo_image, tags = "original_image")
        
        # No need for scroll region since image is scaled to fit
        self.original_canvas.config(scrollregion = (0, 0, canvas_width, canvas_height))
        
        # Add info text showing original size and scale
        scale_percent = int(scale * 100)
        info_text = f"原圖: {img_width}×{img_height} ({scale_percent}%)"
        self.original_canvas.create_text(
            10, canvas_height - 5,
            text = info_text,
            fill = "#8E8E79",
            font = ("Segoe UI", 9),
            anchor = "sw",
            tags = ("info_text", "overlay")
        )
        
        # Store scale for coordinate conversion
        self.original_preview_scale = scale
        self.original_preview_offset = (x_offset, y_offset)
        
        DEBUG("Original preview updated with scaled image: {}×{} -> {}×{} ({}%)", 
              img_width, img_height, scaled_width, scaled_height, scale_percent)
        
        # Draw labels on original canvas if available
        if hasattr(self, 'original_image_labels') and self.original_image_labels:
            self.draw_labels_on_original_canvas(self.original_image_labels)
        
        # Clear pending image since we've successfully updated
        self.pending_original_image = None
    
    def clear_original_preview(self):
        """Clear the original preview canvas"""
        if not self.SHOW_PREVIEW or not hasattr(self, 'original_canvas') or self.original_canvas is None:
            return
            
        DEBUG("Clearing original preview canvas")
        
        # Clear image display
        self.original_canvas.delete("all")
        
        # Add placeholder text
        self.original_canvas.update_idletasks()
        canvas_width = self.original_canvas.winfo_width()
        canvas_height = self.original_canvas.winfo_height()
        
        self.original_canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text = "無原圖",
            fill = "#8E8E79",
            font = ("Segoe UI", 12),
            tags = "placeholder"
        )
        
        # Reset scroll region
        self.original_canvas.config(scrollregion = (0, 0, canvas_width, canvas_height))
        
        # Clear photo image reference
        self.original_photo_image = None
        
        # Clear pending image
        self.pending_original_image = None

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
    def on_preview_enter(self, event, canvas_type="crop"):
        """Handle mouse enter event on preview canvas - change cursor to magnifier"""
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        if not self.SHOW_PREVIEW or canvas is None or not self.magnifier_enabled:
            return
            
        DEBUG("Mouse entered {} canvas", canvas_type)
        canvas.config(cursor=self.magnifier_cursor)
        
    def on_preview_leave(self, event, canvas_type="crop"):
        """Handle mouse leave event on preview canvas - restore normal cursor"""
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        if not self.SHOW_PREVIEW or canvas is None:
            return
            
        DEBUG("Mouse left {} canvas", canvas_type)
        canvas.config(cursor="")
        
        # Hide magnifier tooltip if visible
        self.hide_magnifier_tooltip()
        
    def on_preview_left_press(self, event, canvas_type="crop"):
        """Handle left mouse press on preview canvas - start drag selection for magnifier"""
        if not self.SHOW_PREVIEW or not self.magnifier_enabled:
            return
        
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        image = self.original_image if canvas_type == "crop" else self.original_image_for_preview
        
        if canvas is None or image is None:
            return
            
        DEBUG("Left press on {} canvas at ({}, {})", canvas_type, event.x, event.y)
        
        # Start magnifier drag selection
        self.preview_magnifier_dragging = True
        self.preview_magnifier_drag_start_x = event.x
        self.preview_magnifier_drag_start_y = event.y
        
        # Hide existing tooltip
        self.hide_magnifier_tooltip()
        
    def on_preview_left_drag(self, event, canvas_type="crop"):
        """Handle left mouse drag on preview canvas - show selection rectangle"""
        if not self.preview_magnifier_dragging:
            return
        
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        if canvas is None:
            return
        
        # Clear previous selection rectangle
        if self.preview_magnifier_selection_rect:
            canvas.delete(self.preview_magnifier_selection_rect)
        
        # Draw selection rectangle with dashed line
        self.preview_magnifier_selection_rect = canvas.create_rectangle(
            self.preview_magnifier_drag_start_x, 
            self.preview_magnifier_drag_start_y,
            event.x, event.y,
            outline="cyan", width=2, dash=(5, 5), tags="magnifier_selection"
        )
        
    def on_preview_left_release(self, event, canvas_type="crop"):
        """Handle left mouse release on preview canvas - decide magnification mode"""
        if not self.preview_magnifier_dragging:
            return
        
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        if canvas is None:
            return
        
        # Clear selection rectangle
        if self.preview_magnifier_selection_rect:
            canvas.delete(self.preview_magnifier_selection_rect)
            self.preview_magnifier_selection_rect = None
        
        # Calculate drag distance
        width = abs(event.x - self.preview_magnifier_drag_start_x)
        height = abs(event.y - self.preview_magnifier_drag_start_y)
        
        DEBUG("Left release on {} canvas: drag size {}x{}", canvas_type, width, height)
        
        # Determine if this was a click or a drag
        if width < 5 and height < 5:
            # Small movement - treat as click, use original magnifier logic
            self.show_magnifier_tooltip(event.x, event.y, canvas_type)

            # Show position marker on main canvas
            self._show_click_position_on_main_canvas(event.x, event.y, canvas_type)
        else:
            # Any drag - always use the actual dragged region size
            self.show_magnifier_for_region(
                self.preview_magnifier_drag_start_x,
                self.preview_magnifier_drag_start_y,
                event.x, event.y, canvas_type
            )

        # Reset drag state
        self.preview_magnifier_dragging = False
        
    def show_magnifier_tooltip(self, canvas_x, canvas_y, canvas_type="crop"):
        """Create and show magnifier tooltip with 3x zoomed region
        
        Args:
            canvas_x, canvas_y: Click position on preview canvas
            canvas_type: Either "crop" or "original"
        """
        image = self.original_image if canvas_type == "crop" else self.original_image_for_preview
        if not image:
            DEBUG("No {} image available for magnification", canvas_type)
            return
            
        try:
            from PIL import Image, ImageTk
            
            # Convert canvas coordinates to original image coordinates
            img_x, img_y = self.canvas_to_image_coords(canvas_x, canvas_y, canvas_type)
            if img_x is None or img_y is None:
                DEBUG("Invalid coordinates for magnification")
                return
                
            # Extract magnified region from original image using configured parameters
            magnified_image = self.extract_magnified_region(
                img_x, img_y, 
                zoom_factor=self.magnifier_zoom_factor,
                region_size=self.magnifier_region_size,
                canvas_type=canvas_type
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
            tooltip_x, tooltip_y = self.calculate_tooltip_position(canvas_x, canvas_y, canvas_type)
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

    def show_preview_click_marker(self, canvas_x, canvas_y):
        """Show a crosshair marker on main canvas at the specified position

        Uses double border design (black outer + bright green inner) for maximum visibility.

        Args:
            canvas_x, canvas_y: Coordinates on main canvas where to show marker
        """
        # Hide existing marker first
        self.hide_preview_click_marker()

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            DEBUG("Canvas not ready yet, skipping marker display")
            return

        # Marker configuration
        line_length = 50
        outer_width = 6
        inner_width = 3
        outer_color = "#000000"  # Black
        inner_color = "#00FF00"  # Bright green
        circle_radius = 6

        # Outer layer (black) - horizontal
        h_outer = self.canvas.create_line(
            canvas_x - line_length, canvas_y,
            canvas_x + line_length, canvas_y,
            fill=outer_color, width=outer_width,
            tags="preview_click_marker"
        )
        # Outer layer (black) - vertical
        v_outer = self.canvas.create_line(
            canvas_x, canvas_y - line_length,
            canvas_x, canvas_y + line_length,
            fill=outer_color, width=outer_width,
            tags="preview_click_marker"
        )

        # Inner layer (bright green) - horizontal
        h_inner = self.canvas.create_line(
            canvas_x - line_length, canvas_y,
            canvas_x + line_length, canvas_y,
            fill=inner_color, width=inner_width,
            tags="preview_click_marker"
        )
        # Inner layer (bright green) - vertical
        v_inner = self.canvas.create_line(
            canvas_x, canvas_y - line_length,
            canvas_x, canvas_y + line_length,
            fill=inner_color, width=inner_width,
            tags="preview_click_marker"
        )

        # Center circle with double border
        circle_outer = self.canvas.create_oval(
            canvas_x - circle_radius, canvas_y - circle_radius,
            canvas_x + circle_radius, canvas_y + circle_radius,
            outline=outer_color, width=3, tags="preview_click_marker"
        )
        circle_inner = self.canvas.create_oval(
            canvas_x - circle_radius + 1, canvas_y - circle_radius + 1,
            canvas_x + circle_radius - 1, canvas_y + circle_radius - 1,
            outline=inner_color, width=2, tags="preview_click_marker"
        )

        # Store marker IDs
        marker_ids = [h_outer, v_outer, h_inner, v_inner, circle_outer, circle_inner]
        self.preview_click_marker_lines = marker_ids
        self.preview_click_marker_visible = True

        # Ensure marker is on top
        self.canvas.tag_raise("preview_click_marker")

        DEBUG("Preview click marker shown at ({}, {})", canvas_x, canvas_y)

    def hide_preview_click_marker(self):
        """Hide preview click marker from main canvas"""
        if self.preview_click_marker_visible and self.preview_click_marker_lines:
            for line_id in self.preview_click_marker_lines:
                try:
                    self.canvas.delete(line_id)
                except:
                    pass
            self.preview_click_marker_lines = []
            self.preview_click_marker_visible = False
            DEBUG("Preview click marker hidden")

        # Also delete by tags as a safety measure
        self.canvas.delete("preview_click_marker")

    def _show_click_position_on_main_canvas(self, preview_canvas_x, preview_canvas_y, canvas_type="crop"):
        """Convert preview canvas click to main canvas position and show marker

        Args:
            preview_canvas_x, preview_canvas_y: Click position on preview canvas
            canvas_type: Either "crop" or "original"
        """
        try:
            # Step 1: Convert preview canvas coordinates to original image pixel coordinates
            img_x, img_y = self.canvas_to_image_coords(preview_canvas_x, preview_canvas_y, canvas_type)
            if img_x is None or img_y is None:
                DEBUG("Invalid preview canvas coordinates for marker display")
                return

            # Step 2: Get original image dimensions
            image = self.original_image if canvas_type == "crop" else self.original_image_for_preview
            if not image:
                DEBUG("No image available for coordinate conversion")
                return

            img_width, img_height = image.size

            # Step 3: Convert to YOLO ratio coordinates
            cx_ratio = img_x / img_width
            cy_ratio = img_y / img_height

            DEBUG("Preview click at image coords ({}, {}) = YOLO ratio ({:.4f}, {:.4f})",
                  img_x, img_y, cx_ratio, cy_ratio)

            # Step 4: Convert YOLO ratio to main canvas coordinates
            if not self._ctx:
                DEBUG("No image context available, cannot show marker")
                return

            img_w = self._ctx["img_w"]
            img_h = self._ctx["img_h"]
            sx = self._ctx["sx"]
            sy = self._ctx["sy"]
            ox = self._ctx["ox"]
            oy = self._ctx["oy"]
            disp_w = self._ctx["disp_w"]
            disp_h = self._ctx["disp_h"]

            # Convert YOLO ratio to display coordinates
            display_x = cx_ratio * disp_w
            display_y = cy_ratio * disp_h

            # Apply offset for black borders
            main_canvas_x = display_x + ox
            main_canvas_y = display_y + oy

            DEBUG("Main canvas position: ({:.1f}, {:.1f})", main_canvas_x, main_canvas_y)

            # Step 5: Show marker on main canvas
            self.show_preview_click_marker(main_canvas_x, main_canvas_y)

        except Exception as e:
            ERROR("Failed to show click position on main canvas: {}", str(e))

    def canvas_to_image_coords(self, canvas_x, canvas_y, canvas_type="crop"):
        """Convert preview canvas coordinates to original image coordinates
        
        Args:
            canvas_x, canvas_y: Coordinates on preview canvas
            canvas_type: Either "crop" or "original"
            
        Returns:
            tuple: (img_x, img_y) in original image coordinates, or (None, None) if invalid
        """
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        image = self.original_image if canvas_type == "crop" else self.original_image_for_preview
        photo_image = self.preview_photo_image if canvas_type == "crop" else self.original_photo_image
        
        if not image or not photo_image:
            return None, None
            
        try:
            # Get original image dimensions
            img_width, img_height = image.size
            
            if canvas_type == "crop":
                # Crop canvas: image may be zoomed, account for scrolling and zoom scale
                canvas_x_scroll = canvas.canvasx(canvas_x)
                canvas_y_scroll = canvas.canvasy(canvas_y)

                # Apply inverse zoom scale to get original image coordinates
                zoom_scale = getattr(self, 'preview_zoom_scale', 1.0)
                img_x = int(canvas_x_scroll / zoom_scale)
                img_y = int(canvas_y_scroll / zoom_scale)
            else:
                # Original canvas: image is scaled and centered
                if hasattr(self, 'original_preview_scale') and hasattr(self, 'original_preview_offset'):
                    x_offset, y_offset = self.original_preview_offset
                    scale = self.original_preview_scale
                    
                    # Convert canvas coordinates to scaled image coordinates
                    scaled_x = canvas_x - x_offset
                    scaled_y = canvas_y - y_offset
                    
                    # Convert scaled coordinates to original image coordinates
                    img_x = int(scaled_x / scale)
                    img_y = int(scaled_y / scale)
                else:
                    return None, None
            
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
            
    def extract_magnified_region(self, center_x, center_y, zoom_factor=3.0, region_size=50, canvas_type="crop"):
        """Extract and magnify a region from original image with caching
        
        Args:
            center_x, center_y: Center point in original image coordinates
            zoom_factor: Magnification factor (default 3x)
            region_size: Size of region to extract in pixels
            canvas_type: Either "crop" or "original"
            
        Returns:
            ImageTk.PhotoImage: Magnified region image, or None if failed
        """
        image = self.original_image if canvas_type == "crop" else self.original_image_for_preview
        if not image:
            return None
            
        # Generate cache key based on position and parameters
        cache_key = f"{center_x}_{center_y}_{zoom_factor}_{region_size}_{id(image)}_{canvas_type}"
        
        # Check cache first
        cached_result = self.get_from_magnifier_cache(cache_key)
        if cached_result:
            DEBUG("Using cached magnified region for key: {}", cache_key)
            return cached_result
            
        try:
            from PIL import Image, ImageTk
            
            img_width, img_height = image.size
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
            region = image.crop((left, top, right, bottom))
            
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
        
        # Initialize cache attributes if they don't exist
        if not hasattr(self, 'magnifier_cache'):
            self.magnifier_cache = {}
        if not hasattr(self, 'cache_access_order'):
            self.cache_access_order = []
        
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
        
        # Initialize cache attributes if they don't exist
        if not hasattr(self, 'magnifier_cache'):
            self.magnifier_cache = {}
        if not hasattr(self, 'cache_access_order'):
            self.cache_access_order = []
        if not hasattr(self, 'max_cache_size'):
            self.max_cache_size = 50  # Default cache size
        
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
        
        # Initialize cache attributes if they don't exist
        if not hasattr(self, 'magnifier_cache'):
            self.magnifier_cache = {}
        if not hasattr(self, 'cache_access_order'):
            self.cache_access_order = []
            
        self.magnifier_cache.clear()
        self.cache_access_order.clear()
        DEBUG("Magnifier cache cleared")
            
    def calculate_tooltip_position(self, canvas_x, canvas_y, canvas_type="crop"):
        """Calculate optimal tooltip position for multi-monitor setup
        
        Args:
            canvas_x, canvas_y: Click position on canvas
            canvas_type: Either "crop" or "original"
            
        Returns:
            tuple: (x, y) screen coordinates for tooltip
        """
        try:
            # Get the correct canvas based on canvas_type
            canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
            if not canvas:
                # Fallback to main canvas if preview canvas not available
                canvas = self.canvas if hasattr(self, 'canvas') else None
            
            # Get canvas absolute position on screen (SAME FIX AS calculate_tooltip_position_for_region)
            try:
                if canvas:
                    # Use rootx/rooty to get absolute screen position
                    canvas_screen_x = canvas.winfo_rootx()
                    canvas_screen_y = canvas.winfo_rooty()
                else:
                    # Fallback to window position if canvas not available
                    canvas_screen_x = self.window.winfo_rootx()
                    canvas_screen_y = self.window.winfo_rooty()
            except Exception as e:
                DEBUG("Failed to get canvas screen position: {}", str(e))
                # Ultimate fallback
                canvas_screen_x = 100
                canvas_screen_y = 100
            
            # Calculate tooltip position using screen coordinates (simplified)
            tooltip_x = canvas_screen_x + canvas_x + 20
            tooltip_y = canvas_screen_y + canvas_y + 20
            
            # Get window bounds for boundary checking
            window_x = self.window.winfo_x()
            window_y = self.window.winfo_y()
            window_width = self.window.winfo_width()
            window_height = self.window.winfo_height()
            
            # Estimate tooltip size (smaller for click magnification)
            estimated_width = 200  # Smaller default for click magnification
            estimated_height = 200
            
            # Keep tooltip within window bounds
            window_right = window_x + window_width
            window_bottom = window_y + window_height
            
            # Adjust horizontally if tooltip goes beyond window right edge
            if tooltip_x + estimated_width > window_right:
                # Try placing on the left side of cursor
                alt_x = canvas_screen_x + canvas_x - estimated_width - 20
                if alt_x >= window_x:
                    tooltip_x = alt_x
                else:
                    # If still not enough space, center within window
                    tooltip_x = window_x + (window_width - estimated_width) // 2
            
            # Adjust vertically if tooltip goes beyond window bottom edge
            if tooltip_y + estimated_height > window_bottom:
                # Try placing above cursor
                alt_y = canvas_screen_y + canvas_y - estimated_height - 20
                if alt_y >= window_y:
                    tooltip_y = alt_y
                else:
                    # If still not enough space, center within window
                    tooltip_y = window_y + (window_height - estimated_height) // 2
            
            # Final bounds check - ensure tooltip stays within window
            tooltip_x = max(window_x, min(tooltip_x, window_right - estimated_width))
            tooltip_y = max(window_y, min(tooltip_y, window_bottom - estimated_height))
            
            DEBUG("Tooltip position calculated: window=({},{},{},{}), tooltip=({},{})", 
                  window_x, window_y, window_width, window_height, tooltip_x, tooltip_y)
            
            return tooltip_x, tooltip_y
            
        except Exception as e:
            ERROR("Failed to calculate tooltip position: {}, using fallback", str(e))
            # Fallback to simple offset using screen coordinates
            try:
                canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
                if not canvas:
                    canvas = self.canvas if hasattr(self, 'canvas') else None
                
                if canvas:
                    # Use screen coordinates for fallback too
                    canvas_abs_x = canvas.winfo_rootx()
                    canvas_abs_y = canvas.winfo_rooty()
                    return canvas_abs_x + canvas_x + 20, canvas_abs_y + canvas_y + 20
                else:
                    return 100, 100
            except:
                return 100, 100  # Ultimate fallback
    
    def calculate_tooltip_position_for_region(self, x1, y1, x2, y2, tooltip_width, tooltip_height, canvas_type="crop"):
        """Calculate tooltip position for region selection that doesn't cover the selection
        
        Args:
            x1, y1: Start point of selection (drag start - click origin)
            x2, y2: End point of selection  
            tooltip_width, tooltip_height: Actual size of tooltip
            canvas_type: Either "crop" or "original"
            
        Returns:
            tuple: (x, y) position for tooltip that doesn't cover selection
        """
        try:
            # Get canvas based on type
            canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
            if not canvas:
                canvas = self.canvas if hasattr(self, 'canvas') else None
            
            # Get canvas absolute position on screen (CRITICAL FIX!)
            try:
                if canvas:
                    # Use rootx/rooty to get absolute screen position
                    canvas_screen_x = canvas.winfo_rootx()
                    canvas_screen_y = canvas.winfo_rooty()
                else:
                    # Fallback to window position if canvas not available
                    canvas_screen_x = self.window.winfo_rootx()
                    canvas_screen_y = self.window.winfo_rooty()
            except Exception as e:
                DEBUG("Failed to get canvas screen position: {}", str(e))
                # Ultimate fallback
                canvas_screen_x = 100
                canvas_screen_y = 100
            
            # Calculate selection bounds in screen coordinates
            sel_left = canvas_screen_x + min(x1, x2)
            sel_top = canvas_screen_y + min(y1, y2)
            sel_right = canvas_screen_x + max(x1, x2)
            sel_bottom = canvas_screen_y + max(y1, y2)
            
            # Start position in screen coordinates (click origin point)
            start_x = canvas_screen_x + x1
            start_y = canvas_screen_y + y1
            
            # Get window bounds for boundary checking
            window_x = self.window.winfo_x()
            window_y = self.window.winfo_y()
            window_width = self.window.winfo_width()
            window_height = self.window.winfo_height()
            
            # Try different positions in priority order - prioritize positions near start point
            positions = []
            
            # 1. HIGHEST PRIORITY: Positions near the start point (small offset)
            positions.extend([
                (start_x + 20, start_y + 20),  # Bottom-right of start (most common)
                (start_x - tooltip_width - 20, start_y + 20),  # Bottom-left of start
                (start_x + 20, start_y - tooltip_height - 20),  # Top-right of start
                (start_x - tooltip_width - 20, start_y - tooltip_height - 20)  # Top-left of start
            ])
            
            # 2. MEDIUM PRIORITY: Diagonal positions based on drag direction (avoid selection)
            if x2 >= x1 and y2 >= y1:  # Dragged to bottom-right
                # Place tooltip top-left of start to avoid bottom-right selection
                positions.append((start_x - tooltip_width - 30, start_y - tooltip_height - 30))
            elif x2 < x1 and y2 >= y1:  # Dragged to bottom-left
                # Place tooltip top-right of start to avoid bottom-left selection
                positions.append((start_x + 30, start_y - tooltip_height - 30))
            elif x2 >= x1 and y2 < y1:  # Dragged to top-right
                # Place tooltip bottom-left of start to avoid top-right selection
                positions.append((start_x - tooltip_width - 30, start_y + 30))
            else:  # Dragged to top-left
                # Place tooltip bottom-right of start to avoid top-left selection
                positions.append((start_x + 30, start_y + 30))
            
            # 3. FALLBACK: If start point area is blocked, use selection edges (keeping start point alignment)
            positions.extend([
                (sel_right + 10, start_y),  # Right of selection, start point level
                (sel_left - tooltip_width - 10, start_y),  # Left of selection, start point level
                (start_x, sel_bottom + 10),  # Below selection, start point column
                (start_x, sel_top - tooltip_height - 10),  # Above selection, start point column
            ])
            
            # 4. LAST RESORT: Selection corners (furthest from start point)
            positions.extend([
                (sel_right + 10, sel_top),  # Top-right corner of selection
                (sel_right + 10, sel_bottom - tooltip_height),  # Bottom-right corner
                (sel_left - tooltip_width - 10, sel_top),  # Top-left corner
                (sel_left - tooltip_width - 10, sel_bottom - tooltip_height)  # Bottom-left corner
            ])
            
            # Window bounds
            window_right = window_x + window_width
            window_bottom = window_y + window_height
            
            # Find the first position that fits within window bounds
            for i, (pos_x, pos_y) in enumerate(positions):
                # Check if position is within window bounds
                if not (pos_x >= window_x and 
                       pos_y >= window_y and 
                       pos_x + tooltip_width <= window_right and 
                       pos_y + tooltip_height <= window_bottom):
                    continue
                
                # For positions near start point (first 4 positions), check overlap with selection
                if i < 4:  # High priority positions near start point
                    # Calculate tooltip bounds (all in screen coordinates now)
                    tooltip_left = pos_x
                    tooltip_right = pos_x + tooltip_width
                    tooltip_top = pos_y
                    tooltip_bottom = pos_y + tooltip_height
                    
                    # Selection bounds already in screen coordinates (sel_left, sel_top, sel_right, sel_bottom)
                    # Check overlap directly
                    overlap_x = max(0, min(tooltip_right, sel_right) - max(tooltip_left, sel_left))
                    overlap_y = max(0, min(tooltip_bottom, sel_bottom) - max(tooltip_top, sel_top))
                    overlap_area = overlap_x * overlap_y
                    
                    # Calculate areas for comparison
                    selection_width = abs(x2 - x1)
                    selection_height = abs(y2 - y1)
                    selection_area = selection_width * selection_height
                    tooltip_area = tooltip_width * tooltip_height
                    
                    # Allow position if overlap is small (< 15% of smaller area)
                    smaller_area = min(selection_area, tooltip_area)
                    if smaller_area > 0 and overlap_area < smaller_area * 0.15:
                        DEBUG("Tooltip positioned near start point ({}, {}) with minimal overlap for selection ({},{}) to ({},{})", 
                              pos_x, pos_y, x1, y1, x2, y2)
                        return pos_x, pos_y
                    else:
                        DEBUG("Position ({}, {}) rejected due to significant overlap: {}px² vs threshold {}px²", 
                              pos_x, pos_y, overlap_area, smaller_area * 0.15 if smaller_area > 0 else 0)
                        continue
                else:
                    # For positions away from start point, no overlap check needed (they're designed to avoid selection)
                    DEBUG("Tooltip positioned away from start point ({}, {}) for selection ({},{}) to ({},{})", 
                          pos_x, pos_y, x1, y1, x2, y2)
                    return pos_x, pos_y
            
            # Ultimate fallback: center in window
            fallback_x = window_x + max(0, (window_width - tooltip_width) // 2)
            fallback_y = window_y + max(0, (window_height - tooltip_height) // 2)
            
            DEBUG("Using fallback position ({}, {}) for tooltip", fallback_x, fallback_y)
            return fallback_x, fallback_y
            
        except Exception as e:
            ERROR("Failed to calculate tooltip position for region: {}, using simple fallback", str(e))
            # Simple fallback to original calculation
            return self.calculate_tooltip_position(x1, y1, canvas_type)
        
    def show_magnifier_for_region(self, x1, y1, x2, y2, canvas_type="crop"):
        """Show magnifier for a selected region (drag area)
        
        Args:
            x1, y1: Start coordinates of selection on canvas
            x2, y2: End coordinates of selection on canvas
            canvas_type: Either "crop" or "original"
        """
        image = self.original_image if canvas_type == "crop" else self.original_image_for_preview
        if not image:
            DEBUG("No {} image available for region magnification", canvas_type)
            return
            
        try:
            from PIL import Image, ImageTk
            
            # Ensure coordinates are in correct order
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            # Convert canvas coordinates to image coordinates
            img_left, img_top = self.canvas_to_image_coords(left, top, canvas_type)
            img_right, img_bottom = self.canvas_to_image_coords(right, bottom, canvas_type)
            
            if img_left is None or img_top is None or img_right is None or img_bottom is None:
                DEBUG("Invalid coordinates for region magnification")
                return
            
            # Ensure image coordinates are in bounds
            img_width, img_height = image.size
            img_left = max(0, min(img_width, img_left))
            img_top = max(0, min(img_height, img_top))
            img_right = max(0, min(img_width, img_right))
            img_bottom = max(0, min(img_height, img_bottom))
            
            # Extract the selected region from original image
            region_width = abs(img_right - img_left)
            region_height = abs(img_bottom - img_top)
            
            if region_width < 1 or region_height < 1:
                DEBUG("Region too small for magnification: {}x{}", region_width, region_height)
                return
            
            # Crop the region from the original image
            region = image.crop((img_left, img_top, img_right, img_bottom))
            
            # Calculate appropriate zoom factor based on screen size instead of fixed tooltip size
            try:
                # Get screen dimensions (with fallback)
                screen_width = self.window.winfo_screenwidth() if hasattr(self.window, 'winfo_screenwidth') else 1920
                screen_height = self.window.winfo_screenheight() if hasattr(self.window, 'winfo_screenheight') else 1080
            except:
                # Fallback to common screen resolution
                screen_width, screen_height = 1920, 1080
            
            # Use 80% of screen size as maximum window size
            max_window_width = int(screen_width * 0.8)
            max_window_height = int(screen_height * 0.8)
            
            # Calculate scaling factors based on screen limits
            width_scale = max_window_width / region_width
            height_scale = max_window_height / region_height
            
            # Use the configured zoom factor as the preferred scaling, but don't exceed screen limits
            preferred_zoom = self.magnifier_zoom_factor
            zoom_factor = min(preferred_zoom, width_scale, height_scale)
            
            # Ensure minimum zoom (don't make images smaller than original)
            zoom_factor = max(1.0, zoom_factor)
            
            # Calculate magnified size
            magnified_width = max(1, int(region_width * zoom_factor))
            magnified_height = max(1, int(region_height * zoom_factor))
            
            # Resize the region with high quality
            magnified_region = region.resize(
                (magnified_width, magnified_height), 
                Image.Resampling.LANCZOS
            )
            
            # Convert to PhotoImage
            photo_image = ImageTk.PhotoImage(magnified_region)
            
            # Create magnifier tooltip window
            self.magnifier_tooltip = tk.Toplevel(self.window)
            self.magnifier_tooltip.wm_overrideredirect(True)  # Remove window decorations
            self.magnifier_tooltip.configure(bg="black", bd=2, relief="solid")
            
            # Create label for magnified region
            tooltip_label = tk.Label(self.magnifier_tooltip, image=photo_image, bg="black")
            tooltip_label.pack()
            
            # Update to get actual window size after packing
            self.magnifier_tooltip.update_idletasks()
            
            # Get actual tooltip dimensions
            try:
                actual_width = self.magnifier_tooltip.winfo_width()
                actual_height = self.magnifier_tooltip.winfo_height()
                
                # Ensure we have valid dimensions
                if actual_width <= 1 or actual_height <= 1:
                    # Fallback to photo dimensions if window size not available yet
                    actual_width = magnified_width + 4  # Account for border
                    actual_height = magnified_height + 4
            except:
                # Final fallback
                actual_width = magnified_width + 4
                actual_height = magnified_height + 4
            
            # Calculate tooltip position that doesn't cover the selection area
            tooltip_x, tooltip_y = self.calculate_tooltip_position_for_region(
                x1, y1, x2, y2, 
                actual_width, actual_height, 
                canvas_type
            )
            
            self.magnifier_tooltip.geometry(f"+{tooltip_x}+{tooltip_y}")
            
            # Store image reference to prevent garbage collection
            self.magnifier_tooltip.image = photo_image
            
            DEBUG("Region magnifier shown: region {}x{} -> magnified {}x{} (zoom: {:.2f})", 
                  region_width, region_height, magnified_width, magnified_height, zoom_factor)
                  
            # Dispatch magnifier show event
            if self.dispatch:
                self.dispatch(UIEvent.MAGNIFIER_SHOW, {
                    "canvas_x": (x1 + x2) // 2,
                    "canvas_y": (y1 + y2) // 2,
                    "image_x": (img_left + img_right) // 2,
                    "image_y": (img_top + img_bottom) // 2,
                    "region_size": (region_width, region_height),
                    "zoom_factor": zoom_factor
                })
                  
        except Exception as e:
            ERROR("Failed to show region magnifier: {}", str(e))
        
    def on_preview_right_drag_start(self, event, canvas_type="crop"):
        """Handle right mouse button press - start dragging if image is larger than canvas"""
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        if not self.SHOW_PREVIEW or canvas is None or not self.is_image_draggable(canvas_type):
            return
            
        DEBUG("Right drag start on {} canvas at ({}, {})", canvas_type, event.x, event.y)
        if canvas_type == "crop":
            self.is_dragging_preview = True
        else:
            self.is_dragging_original = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Change cursor to indicate dragging mode
        canvas.config(cursor="fleur")
        
        # Dispatch preview drag start event
        if self.dispatch:
            self.dispatch(UIEvent.PREVIEW_DRAG_START, {
                "x": event.x,
                "y": event.y,
                "canvas_type": canvas_type
            })
        
    def on_preview_right_drag(self, event, canvas_type="crop"):
        """Handle right mouse drag - update image position"""
        is_dragging = self.is_dragging_preview if canvas_type == "crop" else self.is_dragging_original
        if not is_dragging or not self.SHOW_PREVIEW:
            return
            
        # Calculate drag offset
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        DEBUG("Right drag on {} canvas: dx={}, dy={}", canvas_type, dx, dy)
        
        # Update preview view position
        self.update_preview_view(dx, dy, canvas_type)
        
        # Update drag start position for next iteration
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Dispatch preview drag event
        if self.dispatch:
            self.dispatch(UIEvent.PREVIEW_DRAG, {
                "x": event.x,
                "y": event.y,
                "dx": dx,
                "dy": dy,
                "canvas_type": canvas_type
            })
        
    def on_preview_right_drag_end(self, event, canvas_type="crop"):
        """Handle right mouse button release - end dragging"""
        is_dragging = self.is_dragging_preview if canvas_type == "crop" else self.is_dragging_original
        canvas = self.preview_canvas if canvas_type == "crop" else self.original_canvas
        
        if not is_dragging:
            return
            
        DEBUG("Right drag end on {} canvas", canvas_type)
        if canvas_type == "crop":
            self.is_dragging_preview = False
        else:
            self.is_dragging_original = False
        
        # Restore magnifier cursor
        canvas.config(cursor=self.magnifier_cursor)
        
        # Dispatch preview drag end event
        if self.dispatch:
            self.dispatch(UIEvent.PREVIEW_DRAG_END, {
                "x": event.x,
                "y": event.y,
                "canvas_type": canvas_type
            })
        
    def is_image_draggable(self, canvas_type="crop"):
        """Check if current image is large enough to support dragging
        
        Args:
            canvas_type: Either "crop" or "original"
            
        Returns:
            bool: True if image can be dragged, False otherwise
        """
        # Original canvas images are always scaled to fit, so never draggable
        if canvas_type == "original":
            return False
            
        canvas = self.preview_canvas
        image = self.original_image
        photo_image = self.preview_photo_image
        
        if not image or not photo_image or not canvas:
            return False
            
        try:
            # Get original image dimensions
            img_width, img_height = image.size
            
            # Get actual preview canvas dimensions
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # Image is draggable if it's larger than canvas in either dimension
            draggable = img_width > canvas_width or img_height > canvas_height
            
            DEBUG("Image draggable check ({}): {}x{} vs canvas {}x{} -> {}", 
                  canvas_type, img_width, img_height, canvas_width, canvas_height, draggable)
                  
            return draggable
            
        except Exception as e:
            ERROR("Failed to check if image is draggable: {}", str(e))
            return False
            
    def update_preview_view(self, dx, dy, canvas_type="crop"):
        """Update preview canvas view position based on drag offset
        
        Args:
            dx, dy: Drag offset in pixels
            canvas_type: Either "crop" or "original"
        """
        # Original canvas doesn't support dragging as images are scaled to fit
        if canvas_type == "original":
            return
            
        canvas = self.preview_canvas
        if not self.SHOW_PREVIEW or canvas is None:
            return
            
        try:
            # Get current scroll position (0.0 to 1.0)
            current_x_top, current_x_bottom = canvas.xview()
            current_y_top, current_y_bottom = canvas.yview()
            
            # Calculate scroll region dimensions
            scroll_region = canvas.cget("scrollregion").split()
            if len(scroll_region) != 4:
                return
                
            total_width = float(scroll_region[2]) - float(scroll_region[0])
            total_height = float(scroll_region[3]) - float(scroll_region[1])
            
            # Calculate canvas dimensions
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
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
                canvas.xview_moveto(new_x_top)
            if total_height > canvas_height:
                canvas.yview_moveto(new_y_top)
                
            DEBUG("Updated {} view: x={:.3f}, y={:.3f}", canvas_type, new_x_top, new_y_top)
            
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
        
        
        
# Add an adjustable vertival Line to cut image


        
    def create_vertical_line(self):
        if not self.SHOW_CUT_IMAGE:
            return
        
        def on_vertical_line_press(line, event):
            if self.dispatch:
                self.dispatch(UIEvent.VERTICAL_LINE_PRESS, None)
                DEBUG("Vertical line pressed, event dispatched")
      
        # Create two draggable lines with different styles
        self.cut_line = DraggableVerticalLine(
        self.canvas,
            x=800,
            foreground="#cccccc",# 淺線     
            background="#333333",# 深線     
            width_fg=6,
            width_bg=10,
            bounds= None,
            snap=1,
            # on_move=self.on_line_move,
            on_move=None,
            on_press=on_vertical_line_press
         )
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
        # Ensure minimum canvas size to prevent resize errors
        if self.canvas_height <= 10 or self.canvas_width <= 10:
            self.canvas_height = 720
            self.canvas_width = 1920
            DEBUG("Canvas too small, using default size: {}x{}", self.canvas_width, self.canvas_height)
        return self.canvas_height, self.canvas_width
    
    def on_canvas_resize(self, event):
        if self.dispatch:
            self.dispatch(UIEvent.CANVAS_RESIZE, {})
            

    def cut_image(self, event):
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        if not self.SHOW_CUT_IMAGE:
            return

        print("Cut image event triggered")
        # Check if self.cut_line exists
        if hasattr(self, 'cut_line') and self.cut_line is not None:
            # Get the position of the cut line
            position = self.cut_line.get_x()
            self.dispatch(UIEvent.CUT_IMAGE, {"position": position})

            # Add your logic here to handle the cut line position
        else:
            print("Cut line does not exist.")
        
    def update_image_canvas(self, image= None):
        DEBUG("update_image_canvas")
        self.canvas.delete("all")
        if not image:
            DEBUG("No image provided to update canvas")
            return
        self.canvas.image = image
        self.canvas.create_image(self.canvas_width//2, self.canvas_height//2, anchor = "center",
                                  image = self.canvas.image, tags="bg_image")
        DEBUG("Image updated on canvas with height: {}, width: {}", self.canvas_height, self.canvas_width)
        self.create_vertical_line()

        try:
            if self.bbox_controller and hasattr(self.canvas, "image") and self.canvas.image:
                disp_w = int(self.canvas.image.width())   # Tk PhotoImage 的實際寬度（顯示到主畫布的影像寬）
                # 原圖寬度優先用 set_original_image() 傳進來的原圖；退而求其次用 controller 早前塞的值
                if self.original_image is not None:
                    orig_w = self.original_image.size[0]
                else:
                    orig_w = getattr(self.bbox_controller, "original_image_width", disp_w)
                scale_x = float(disp_w) / float(orig_w) if orig_w else 1.0
                self.bbox_controller.display_scale_x = scale_x
                DEBUG("display_scale_x updated: disp_w={}, orig_w={}, scale_x={}", disp_w, orig_w, scale_x)
        except Exception as e:
            ERROR("Failed to update display_scale_x: {}", str(e))

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


    def set_image_context(self, ctx_dict):
        self._ctx = ctx_dict
        # Pass context to bbox_controller for coordinate handling
        if self.bbox_controller:
            self.bbox_controller.set_image_context(ctx_dict)


    def draw_labels_on_canvas(self, labels):
        """Draw label bounding boxes on canvas with resize handles"""
        # Store current labels for access by other methods (like cursor updates)
        self.current_labels = labels
        
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
            # Get context for coordinate conversion
            if not self._ctx:
                img_w = self.canvas_width
                img_h = self.canvas_height
                sx = sy = 1.0
                ox = oy = 0.0
                disp_w = self.canvas_width
                disp_h = self.canvas_height
            else:
                img_w = self._ctx["img_w"]; img_h = self._ctx["img_h"]
                sx    = self._ctx["sx"];    sy    = self._ctx["sy"]
                ox    = self._ctx["ox"];    oy    = self._ctx["oy"]
                disp_w = self._ctx["disp_w"]
                disp_h = self._ctx["disp_h"]

            # Convert label coordinates to canvas pixel coordinates
            # Use display dimensions for the actual image area (not full canvas)
            x1, y1, x2, y2 = label_display_utils.convert_label_to_canvas_coords(
                label, disp_w, disp_h
            )

            # Apply offset for black borders
            x1 += ox
            y1 += oy
            x2 += ox
            y2 += oy

            actual_bbox_width  = int(label.w_ratio * img_w)
            actual_bbox_height = int(label.h_ratio * img_h)

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
                if actual_bbox_width < self.MIN_BBOX_WIDTH_THRESHOLD:
                    # Warning style: orange/red color for small bbox
                    color = "#FF8B2C"  # OrangeRed color for warning
                    tags = ("label_box", "label_box_warning")

                else:
                    # Not selected: green color
                    color = "#0CC00C"
                    tags = ("label_box",)
                width = 3
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
           
            # Selected labels are highlighted with red border (no handles shown)
            
            # Draw class ID text
            text_x = x1
            text_y = y1 - 15 if y1 > 20 else y2 + 15

            # self.canvas.create_text(
            #     text_x, text_y,
            #     # text=str(label.class_id),
            #     text=wlm.get_label(label.class_id),
            #     fill=color,
            #     anchor="nw",

            #     tags="label_text"
            # )
            font_size = self.LABEL_FONT_SIZE
            color = CLASS_ID_COLOR_MAP.get(label.class_id, "black")
            draw_outlined_text(
                self.canvas,
                text_x, text_y,
                text=wlm.get_label(label.class_id),
                font=("Arial", font_size, "bold"),
                outline_color="white", fill_color=color, thickness=2, tags="label_text")

            # Draw bbox dimensions if enabled
            if self.SHOW_BBOX_DIMENSIONS:
                try:
                    if self.original_image is not None:
                        ow, oh = self.original_image.size
                    else:
                        # fallback：退回舊機制，但不建議
                        from config_utils import get_image_info
                        oh, ow = get_image_info()
                except Exception:
                    # 最後保底：用畫上去的 box 反推（避免整段 fail）
                    ow = max(1, int(x2 - x1))
                    oh = max(1, int(y2 - y1))


                if actual_bbox_width < self.MIN_BBOX_WIDTH_THRESHOLD:
                    dimension_text = f"⚠️ {actual_bbox_width}×{actual_bbox_height}"
                    dim_color = "#FF8B2C"  # Warning yellow
                else:
                    dimension_text = f"{actual_bbox_width}×{actual_bbox_height} "
                    dim_color = color  # Normal color
                
                # Position outside top-right corner to avoid covering box lines
                dim_text_x = x2 + 5
                dim_text_y = y1 - 15 if y1 > 20 else y2 + 15  # Above box
                # If too close to top, put it below the box instead
                
                draw_outlined_text(
                    self.canvas,
                    dim_text_x, dim_text_y,
                    text=dimension_text,
                    font=("Arial", font_size - 2, "normal"),
                    outline_color="white", fill_color=dim_color,
                    thickness=2, tags="label_text")

            DEBUG("Drew label: class_id={}, coords=({:.1f},{:.1f},{:.1f},{:.1f})",
                  label.class_id, x1, y1, x2, y2)

        # Draw tilt angle regression line if enabled
        if self.SHOW_TILT_ANGLE and labels and len(labels) >= 2:
            angle, line_start, line_end = label_display_utils.calculate_plate_tilt_angle(labels)
            if line_start and line_end:
                # Clear previous guideline
                self.canvas.delete("tilt_guideline")

                # Get context for coordinate conversion
                if not self._ctx:
                    img_w = self.canvas_width
                    img_h = self.canvas_height
                    ox = oy = 0.0
                    disp_w = self.canvas_width
                    disp_h = self.canvas_height
                else:
                    img_w = self._ctx["img_w"]; img_h = self._ctx["img_h"]
                    ox = self._ctx["ox"]; oy = self._ctx["oy"]
                    disp_w = self._ctx["disp_w"]
                    disp_h = self._ctx["disp_h"]

                # Convert ratio coordinates to canvas pixel coordinates
                x1_line = line_start[0] * disp_w + ox
                y1_line = line_start[1] * disp_h + oy
                x2_line = line_end[0] * disp_w + ox
                y2_line = line_end[1] * disp_h + oy

                # Draw regression line
                self.canvas.create_line(
                    x1_line, y1_line, x2_line, y2_line,
                    fill="#CCCCCC", width=2, dash=(10, 5),
                    tags="tilt_guideline"
                )
                DEBUG("Drew tilt guideline: ({:.1f},{:.1f}) to ({:.1f},{:.1f})",
                      x1_line, y1_line, x2_line, y2_line)


# Update text and index labels
    def update_text_box(self, content=None):
        if not self.SHOW_TEXT_BOX or self.label_text_box is None:
            DEBUG("Text box is not shown or not initialized.")
            return

        self.label_text_box.unbind("<<Modified>>")

        if not self.SHOW_TEXT_BOX:
            DEBUG("Text box is not shown as per configuration.")
            return
        self.label_text_box.config(state = "normal")
        self.label_text_box.delete("1.0", tk.END) # Clear the text box
        if content is None:
            content = ""
        self.label_text_box.insert(tk.END, content)

        self.label_text_box.edit_modified(False)
        self.label_text_box.bind("<<Modified>>", self.on_text_modified)

    def update_console(self, content=None, plate_data=None):
        """Update console text box with scan results

        Args:
            content (str): Formatted text content to display
            plate_data (list): List of tuples (plate_text, page_num, filename) for clickable lines
        """
        if not self.SHOW_TEXT_BOX or self.console_text_box is None:
            DEBUG("Console is not shown or not initialized.")
            return

        self.console_text_box.config(state="normal")
        self.console_text_box.delete("1.0", tk.END)
        if content is None:
            content = ""
        self.console_text_box.insert(tk.END, content)

        # Add clickable tags for data lines
        if plate_data:
            # Find the line number where data starts (after header lines)
            lines = content.split('\n')
            data_start_line = None
            for i, line in enumerate(lines, start=1):
                if line.startswith('-' * 70):
                    data_start_line = i + 1  # Data starts after separator line
                    break

            if data_start_line:
                for idx, (plate_text, page_num, filename) in enumerate(plate_data):
                    line_num = data_start_line + idx
                    tag_name = f"clickable_{line_num}"

                    # Add tag for this line
                    start_pos = f"{line_num}.0"
                    end_pos = f"{line_num}.end"
                    self.console_text_box.tag_add(tag_name, start_pos, end_pos)

                    # Configure tag appearance (clickable style)
                    self.console_text_box.tag_config(
                        tag_name,
                        foreground="#00ffff",  # Cyan for clickable items
                        underline=True
                    )

                    # Bind click event
                    self.console_text_box.tag_bind(
                        tag_name,
                        "<Button-1>",
                        lambda event, page=page_num, line=line_num: self.on_console_line_click(event, page, line)
                    )

                    # Change cursor on hover
                    self.console_text_box.tag_bind(
                        tag_name,
                        "<Enter>",
                        lambda event: self.console_text_box.config(cursor="hand2")
                    )
                    self.console_text_box.tag_bind(
                        tag_name,
                        "<Leave>",
                        lambda event: self.console_text_box.config(cursor="")
                    )

        self.console_text_box.config(state="disabled")

        # Switch to console tab
        if self.text_notebook:
            self.text_notebook.select(self.console_tab)

    def update_index_label(self, index, path):
        DEBUG("update_index_label")
        # Update total pages for validation
        self.total_pages = len(path)
        # Update current page entry (editable)
        self.index_entry.delete(0, tk.END)
        self.index_entry.insert(0, f"{index + 1}")
        # Update total pages label (read-only)
        self.index_total_label.config(text = f"/{len(path)}")
        DEBUG("Index display updated: {}/{}", index + 1, len(path))

    def update_path_label(self, path):
        self.path_label.config(text = f"{path}")

    def draw_labels_on_original_canvas(self, labels):
        """Draw label bounding boxes on original preview canvas (read-only view)"""
        if not self.original_canvas or not labels:
            return
            
        import label_display_utils
        
        DEBUG("Drawing {} labels on original canvas", len(labels))
        
        # Clear previous label items on original canvas
        self.original_canvas.delete("original_label_box")
        self.original_canvas.delete("original_label_text")
        
        # Get canvas and image dimensions for coordinate conversion
        if not hasattr(self, 'original_preview_scale') or not hasattr(self, 'original_preview_offset'):
            DEBUG("Original preview scale/offset not available, skipping label drawing")
            return
            
        scale = self.original_preview_scale
        x_offset, y_offset = self.original_preview_offset
        
        # Get original image size
        if not self.original_image_for_preview:
            return
        original_width, original_height = self.original_image_for_preview.size
        
        # Define color for original image labels (different from crop labels)
        original_label_color = "#00FFFF"  # Cyan color for original image labels
        
        for label in labels:
            # Convert YOLO coordinates to original image pixel coordinates
            center_x = label.cx_ratio * original_width
            center_y = label.cy_ratio * original_height
            box_width = label.w_ratio * original_width
            box_height = label.h_ratio * original_height
            
            # Convert to canvas coordinates (top-left, bottom-right)
            x1 = (center_x - box_width / 2) * scale + x_offset
            y1 = (center_y - box_height / 2) * scale + y_offset
            x2 = (center_x + box_width / 2) * scale + x_offset
            y2 = (center_y + box_height / 2) * scale + y_offset
            
            # Draw bounding box
            self.original_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=original_label_color,
                width=2,
                tags="original_label_box"
            )
            
            ## Draw class ID text
            #text_x = x1
            #text_y = y1 - 5 if y1 > 15 else y2 + 5
            #
            #self.original_canvas.create_text(
            #    text_x, text_y,
            #    text=str(label.class_id),
            #    fill=original_label_color,
            #    font=("Arial", 10, "bold"),
            #    anchor="nw",
            #    tags="original_label_text"
            #)
        
        DEBUG("Drew {} labels on original canvas", len(labels))

    def highlight_yolo_line_for_label(self, selected_label):
        if not self.label_text_box:
            DEBUG("Text box is not initialized.")
            return

        DEBUG("Highlighting YOLO line for label: {}", selected_label)
        self.label_text_box.tag_remove("highlight", "1.0", tk.END)  # Clear previous highlights

        if not selected_label or not hasattr(selected_label, 'line_index'):
            DEBUG("No valid label selected.")
            return

        line_index = selected_label.line_index
        if line_index is None:
            DEBUG("Label line_index is None, skipping highlight")
            return

        DEBUG("Highlighting line_index {}", line_index)
        start = f"{line_index + 1}.0"
        end = f"{line_index + 1}.end"
        self.label_text_box.tag_add("highlight", start, end)
        self.label_text_box.tag_config("highlight", background="#0C0CC0", foreground="#F0EF43", font = ("Segoe UI", 11, "bold"))

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
                # Add to plate memory
                self.add_to_plate_memory(input_text)
                self.dispatch(UIEvent.INPUT_ENTER, {"text": input_text})
                self.window.focus_set()
            else:
                DEBUG("Input box is empty!")
        else:
            DEBUG("Dispatch is not initialized.")

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

    def add_to_plate_memory(self, plate_text):
        """Add a plate to memory and update button display"""
        if not plate_text or plate_text == "請輸入車牌號碼":
            return

        plate_text = plate_text.strip().upper()
        if not plate_text:
            return

        # Remove if already exists to move it to front
        if plate_text in self.recent_plates:
            self.recent_plates.remove(plate_text)

        # Add to front
        self.recent_plates.appendleft(plate_text)
        DEBUG("Added plate to memory: {}, total: {}", plate_text, len(self.recent_plates))

        # Update button display
        self.update_plate_memory_buttons()

        # Save to config
        self.save_plate_memory_to_config()

    def update_plate_memory_buttons(self):
        """Update the display of plate memory buttons"""
        if not self.plate_memory_frame:
            return

        # Clear existing buttons
        for button in self.plate_memory_buttons:
            button.destroy()
        self.plate_memory_buttons.clear()

        # Create new buttons for each plate in memory
        for plate_text in self.recent_plates:
            btn = tk.Button(
                self.plate_memory_frame,
                text=plate_text,
                font=("Segoe UI", 9),
                bg="#E8E8E8",
                fg="#2D2D2D",
                relief="flat",
                bd=1,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda p=plate_text: self.on_memory_button_click(p)
            )
            btn.pack(side="left", padx=(0, 5))

            # Add hover effects
            def on_enter(e, button=btn):
                button.config(bg="#D0D0D0")
            def on_leave(e, button=btn):
                button.config(bg="#E8E8E8")

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            self.plate_memory_buttons.append(btn)

    def on_memory_button_click(self, plate_text):
        """Handle clicking a plate memory button"""
        if self.input_box:
            # Clear current input and insert selected plate
            self.input_box.delete(0, tk.END)
            self.input_box.insert(0, plate_text)
            self.input_box.config(fg="#2D2D2D")

            # Focus the input box
            self.input_box.focus_set()
            DEBUG("Filled input box with plate from memory: {}", plate_text)

    def add_plate_to_memory_from_controller(self, plate_text):
        """Public method for Controller to add plates to memory"""
        self.add_to_plate_memory(plate_text)

    def load_plate_memory_from_config(self):
        """Load plate memory from config file"""
        try:
            plates_list = config_utils.get_recent_plates()
            # Add plates to deque in reverse order to maintain correct order
            for plate in reversed(plates_list):
                if plate:  # Only add non-empty plates
                    self.recent_plates.appendleft(plate)
            DEBUG("Loaded {} plates from config", len(self.recent_plates))
        except Exception as e:
            DEBUG("Failed to load plate memory from config: {}", e)

    def save_plate_memory_to_config(self):
        """Save current plate memory to config file"""
        try:
            plates_list = list(self.recent_plates)
            config_utils.save_recent_plates(plates_list)
            DEBUG("Saved {} plates to config", len(plates_list))
        except Exception as e:
            ERROR("Failed to save plate memory to config: {}", e)

    def  _on_copy_file_name_text(self, event):
        self.window.clipboard_clear()
        self.window.clipboard_append(self.path_label.cget("text"))
        text = self.path_label.cget("text")
        self.show_info(f"copy file name: {text}")

# Button events    
    def update_timer_display(self, text, color="blue"):
        """Update the timer display in the toolbar
        
        Args:
            text: Text to display (e.g., "10:00" or empty string to hide)
            color: Color of the text (blue, orange, red)
        """
        self.timer_label.config(text=text, fg=color)
    
    def show_info_dialog(self):
        """Show a popup window with usage manual and version (styled like Configuration)"""

        manual_text = (
            "【基本導航】\n"
            "← 上一張\n"
            "→ 下一張\n"
            "Ctrl+F：開啟檔案搜尋\n"
            "\n"
            "【框選操作】\n"
            "滑鼠左鍵：選取box\n"
            "拖曳選中的box：移動box位置\n"
            "拖曳選中的box邊框：調整box大小\n"
            "滑鼠右鍵：刪除選中的box\n"
            "Delete鍵：刪除選中的box\n"
            "\n"
            "【繪製模式】\n"
            "Ctrl：切換繪框模式\n"
            "繪框模式下拖拽：繪製新box\n"
            "\n"
            "【輔助功能】\n"
            "T：快速校正車牌字元\n"
            "Shift+C：裁切圖片（需啟用裁切功能）\n"
            "右Ctrl（按住）：顯示放大鏡\n"
            "\n"
            "※ 標籤會自動依位置排序\n"
        )

        try:
            from constants import VERSION_NUM
            version = VERSION_NUM
        except Exception:
            version = "v0.0.0"

        # === 建立固定大小對話框（同 Configuration 風格） ===
        dialog_width  = 450
        dialog_height = 480

        top = tk.Toplevel(self.window)
        top.title("Info")
        top.geometry(f"{dialog_width}x{dialog_height}")
        top.resizable(False, False)
        top.transient(self.window)
        top.grab_set()

        # === 版面：外層、標題、群組框（圓角淺色）、版本、按鈕列 ===
        main_frame = ttk.Frame(top, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame,
            text="UI Manual",
            font=("Arial", 11, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 操作建議群組框：圓角淺色（ttk.LabelFrame）
        ops_group = ttk.LabelFrame(main_frame, text="操作方式", padding="10")
        ops_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ops_label = ttk.Label(
            ops_group,
            text=manual_text,
            justify="left",
            anchor="nw",
            font=("Arial", 10),
            wraplength=dialog_width - 40
        )
        ops_label.pack(anchor="nw")

        # 版本字樣：放在操作文字下方
        version_row = ttk.Frame(main_frame)
        version_row.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(
            version_row,
            text=f"版本：{version}",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)

        # 底部按鈕列
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="關閉", command=top.destroy).pack(side=tk.RIGHT)

        # === 置中（參考 Configuration 的置中邏輯） ===
        try:
            parent_x = self.window.winfo_rootx()
            parent_y = self.window.winfo_rooty()
            parent_w = self.window.winfo_width()
            parent_h = self.window.winfo_height()
            x = parent_x + (parent_w - dialog_width) // 2
            y = parent_y + (parent_h - dialog_height) // 2
            if x < 0: x = 0
            if y < 0: y = 0
            top.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            top.minsize(dialog_width, dialog_height)
            top.maxsize(dialog_width, dialog_height)
        except Exception:
            pass


    def show_move_menu(self):
        # 取得按鈕在畫面中的位置
        x = self.move_button.winfo_rootx()
        y = self.move_button.winfo_rooty() + self.move_button.winfo_height()
        self.move_menu.tk_popup(x, y)
        
    def on_bt_click_reselect(self):
        DEBUG("on_bt_click_reselect")
        if self.dispatch:
            self.dispatch(UIEvent.SELECT_FOLDERS, {})

    def on_bt_click_crop(self):
        DEBUG("on_bt_click_crop")
        if self.dispatch:
            self.dispatch(UIEvent.CROP_ALL, {})

    def on_cut_image_button_click(self):
        DEBUG("on_cut_image_button_click")
        self.cut_image(None)
            
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

    def on_mouse_motion(self, event):
        """Handle mouse motion event - update cursor based on position"""
        # Check if mouse is near the vertical cut line or dragging it
        if self.SHOW_CUT_IMAGE and hasattr(self, 'cut_line') and self.cut_line is not None:
            # Check if currently dragging the cut line
            if getattr(self.cut_line, '_dragging', False):
                # Don't update cursor when dragging cut line
                return
            # Check if mouse is near the cut line (using same logic as DraggableVerticalLine)
            grab_px = getattr(self.cut_line, 'grab_px', 6)
            if abs(event.x - self.cut_line.get_x()) <= grab_px:
                # Don't update cursor when near cut line
                return
        
        if self.bbox_controller and hasattr(self, 'current_labels') and self.current_labels:
            # Update cursor based on mouse position using stored labels
            self.bbox_controller.update_cursor_for_position(event.x, event.y, self.current_labels)
        
        # Update crosshair auxiliary lines when in drawing mode
        if self.bbox_controller:
            self.bbox_controller.update_crosshair_position(event.x, event.y)

    # Key events
    def toggle_drawing_mode(self, event):
        """Toggle drawing mode"""
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        DEBUG("toggle_drawing_mode triggered")

        # Toggle drawing mode
        if self.bbox_controller:
            self.drawing_mode = self.bbox_controller.toggle_drawing_mode()
            DEBUG("Drawing mode toggled to: {}", self.drawing_mode)

            # Update status display
            self.update_drawing_mode_display()
        else:
            ERROR("bbox_controller is None!")

        if self.dispatch:
            self.dispatch(UIEvent.TOGGLE_DRAWING_MODE, {"value": event, "drawing_mode": self.drawing_mode})

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
        if self.dispatch:
            self.dispatch(UIEvent.WINDOW_POSITION, {})

    def delete_bbox(self, event):
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        DEBUG("delete_bbox")
        if self.dispatch:
            self.dispatch(UIEvent.DELETE_BBOX, {"value": event})
    
    def quick_correct(self, event):
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        DEBUG("quick_correct - Quick correction hotkey pressed")
        if self.dispatch:
            self.dispatch(UIEvent.QUICK_CORRECT, {})

    def delete_image(self, event=None):
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        DEBUG("delete_image")
        if self.dispatch:
            self.dispatch(UIEvent.DELETE_IMAGE,  None)
       
    def on_search_enter(self):
        filename = self.search_entry.get().strip()
        if filename and self.dispatch:
            DEBUG("Search enter with text: {}", filename)
            self.dispatch(UIEvent.SEARCH_FILE, {"filename": filename})
        else:
            DEBUG("Search enter with empty text or dispatch not set")

    def on_index_entry_enter(self):
        """Handle Enter key press in index entry to jump to page"""
        page_text = self.index_entry.get().strip()
        if not page_text:
            DEBUG("Index entry is empty")
            return

        try:
            # Parse input - support "X/Y" format or just "X"
            if "/" in page_text:
                # Extract number before "/"
                page_num = int(page_text.split("/")[0].strip())
            else:
                # Direct number input
                page_num = int(page_text)

            DEBUG("Jump to page request: {}", page_num)

            # Validate range (1-based input)
            if page_num < 1 or page_num > self.total_pages:
                self.show_error(f"頁數必須在 1 到 {self.total_pages} 之間")
                return

            # Trigger jump event
            if self.dispatch:
                self.dispatch(UIEvent.JUMP_TO_PAGE, {"page": page_num})

        except ValueError:
            DEBUG("Invalid page number input: {}", page_text)
            self.show_error("請輸入有效的頁數")

    def search_file(self,event):
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        win_w, win_h = 600, 100
        root_w = self.window.winfo_width()
        root_h = self.window.winfo_height()
        root_x = self.window.winfo_x()
        root_y = self.window.winfo_y()

        # 計算置中位置
        pos_x = root_x + (root_w // 2) - (win_w // 2)
        pos_y = root_y + (root_h // 2) - (win_h // 2) 
        search_win = tk.Toplevel(self.window)
        search_win.title("searching...")
        search_win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
    
        # 輸入框
        self.search_entry = ttk.Entry(search_win, width=80)
        self.search_entry.grid(row=0, column=0, padx=10, pady=20)
    
        # 按鈕 
        def on_enter():
            text = self.search_entry.get()
            search_win.destroy()  # 按下後關閉視窗
    
        btn = ttk.Button(search_win, text="enter", command=self.on_search_enter)
        btn.grid(row=0, column=1, padx=5)
    
        # 自動 focus 到輸入框
        self.search_entry.focus()
            
    def move_to_special_plates(self):
        DEBUG("Move to special plates")
        if self.dispatch:
            self.dispatch(UIEvent.MOVE_IMAGE,  {"plate_types": "SpecialPlates"})
   

    def move_to_uncertain(self):
        DEBUG(" Move to uncertain")      
        if self.dispatch:
            self.dispatch(UIEvent.MOVE_IMAGE,  {"plate_types": "UncertainPlates"})      

    def on_bt_click_batch_sort(self):
        """Handle batch sort button click"""
        DEBUG("on_bt_click_batch_sort")
        if self.dispatch:
            self.dispatch(UIEvent.BATCH_SORT, {})

    def on_bt_click_scan_plates(self):
        """Handle scan plates button click"""
        DEBUG("on_bt_click_scan_plates")
        if self.dispatch:
            self.dispatch(UIEvent.SCAN_UNIQUE_PLATES, {})

    def on_console_line_click(self, event, page_num, line_num):
        """Handle click on console line to jump to corresponding page

        Args:
            event: Tkinter event object
            page_num (int): Page number to jump to (1-based)
            line_num (int): Line number in console text box (1-based)
        """
        DEBUG("Console line clicked: jumping to page {}, highlighting line {}", page_num, line_num)

        # Highlight the clicked line for visual feedback
        if self.console_text_box:
            try:
                # Temporarily enable text box to modify tags
                self.console_text_box.config(state="normal")

                # Clear previous highlight
                self.console_text_box.tag_remove("console_selected", "1.0", tk.END)

                # Add highlight to clicked line
                start_pos = f"{line_num}.0"
                end_pos = f"{line_num}.end"
                self.console_text_box.tag_add("console_selected", start_pos, end_pos)

                # Configure highlight style (yellow background, black text)
                self.console_text_box.tag_config(
                    "console_selected",
                    background="#ffff00",
                    foreground="#000000"
                )

                # Raise tag priority so it appears above clickable style
                self.console_text_box.tag_raise("console_selected")

                # Restore disabled state
                self.console_text_box.config(state="disabled")

            except Exception as e:
                ERROR("Error highlighting console line: {}", e)

        # Dispatch jump event
        if self.dispatch:
            self.dispatch(UIEvent.JUMP_TO_PAGE, {"page": page_num})

    def on_configuration_click(self):
        """Handle configuration button click"""
        DEBUG("on_configuration_click")
        if self.dispatch:
            self.dispatch(UIEvent.OPEN_SETTINGS, None)
    

    def on_text_modified(self, event):
        if self.label_text_box.edit_modified():
            self.label_text_box.edit_modified(False)
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
            self.SHOW_CLASSIFY_FRAME = settings.get('show_classify_frame', False)
            self.SHOW_CUT_IMAGE = settings.get('show_cut_image', True)
            self.SHOW_BBOX_DIMENSIONS = settings.get('show_bbox_dimensions', False)
            self.SHOW_TILT_ANGLE = settings.get('show_tilt_angle', False)
            self.MIN_BBOX_WIDTH_THRESHOLD = settings.get('min_bbox_width_threshold', DEFAULT_MIN_PLATE_WIDTH)
            self.LABEL_FONT_SIZE = settings.get('label_font_size', 12)
            self.PROPORTIONAL_SCALING = settings.get('proportional_scaling', False)
            
            # Update bbox_controller settings for reference box feature
            if self.bbox_controller:
                self.bbox_controller.show_bbox_dimensions = self.SHOW_BBOX_DIMENSIONS
                self.bbox_controller.min_width_threshold = self.MIN_BBOX_WIDTH_THRESHOLD
                
                # Update original image width (in case image has changed)
                original_height, original_width = config_utils.get_image_info()
                self.bbox_controller.original_image_width = original_width
            
            # Apply classification frame visibility
            self.toggle_classification_frame(self.SHOW_CLASSIFY_FRAME)
            
            # Apply cut image visibility
            self.toggle_cut_image(self.SHOW_CUT_IMAGE)
            
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
        """Toggle text box visibility (now using Notebook)"""
        try:
            if show:
                # If we want to show but text_notebook doesn't exist, create it
                if not hasattr(self, 'text_notebook') or self.text_notebook is None:
                    DEBUG("Creating text notebook for show operation")
                    if hasattr(self, 'text_frame'):
                        # Create Notebook (tab control)
                        self.text_notebook = ttk.Notebook(self.text_frame)

                        # Tab 1: Labels
                        self.labels_tab = tk.Frame(self.text_notebook, bg="#FAFAFA")
                        self.text_notebook.add(self.labels_tab, text="Labels")

                        self.label_text_box = tk.Text(
                            self.labels_tab,
                            height=15, bg="#FAFAFA",
                            font=("Segoe UI", 11), fg="#2d2d2d",
                            relief="sunken",
                            wrap="word"
                        )
                        self.label_text_box.tag_configure("left", justify="left")
                        self.label_text_box.pack(fill="both", expand=True)
                        self.label_text_box.bind("<<Modified>>", self.on_text_modified)

                        # Tab 2: Console
                        self.console_tab = tk.Frame(self.text_notebook, bg="#FAFAFA")
                        self.text_notebook.add(self.console_tab, text="Console")

                        self.console_text_box = tk.Text(
                            self.console_tab,
                            height=15, bg="#2d2d2d",
                            font=("Consolas", 10), fg="#00ff00",
                            relief="sunken",
                            wrap="none",
                            state="disabled"
                        )
                        self.console_text_box.pack(fill="both", expand=True)

                # Show the notebook
                if hasattr(self, 'text_notebook') and self.text_notebook:
                    try:
                        # Check if already packed by trying to get pack_info
                        self.text_notebook.pack_info()
                    except tk.TclError:
                        # Not packed, so pack it
                        self.text_notebook.pack(side="top", fill="both", expand=True, padx=20, pady=10)
                        DEBUG("Text notebook shown")
            else:
                # Hide the notebook if it exists
                if hasattr(self, 'text_notebook') and self.text_notebook:
                    try:
                        # Check if packed by trying to get pack_info
                        self.text_notebook.pack_info()
                        # If we get here, it's packed, so forget it
                        self.text_notebook.pack_forget()
                        DEBUG("Text notebook hidden")
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
                        self.input_box.pack(before=self.label_text_box,side="top", fill="x", padx=20, pady=10)
                        DEBUG("Input box shown")
            else:
                # Hide the input box if it exists
                if hasattr(self, 'input_box') and self.input_box:
                    try:
                        # Check if packed by trying to get pack_info
                        self.input_box_pack_info = self.input_box.pack_info()
                        # If we get here, it's packed, so forget it
                        self.input_box.pack_forget()
                        DEBUG("Input box hidden")
                    except tk.TclError:
                        # Already not packed
                        pass
        except Exception as e:
            ERROR("Error toggling input box: {}", e)

    def toggle_classification_frame(self, show):
        """Toggle classification frame visibility"""
        try:
            if show is True:
                # If we want to show but classification_frame doesn't exist, create it
                if not hasattr(self, 'classification_frame') or self.classification_frame is None:
                    DEBUG("Creating classification frame for show operation")
                    # Add classification checkboxes or buttons here if needed
                    self.create_classification_area()
                else:
                    try:
                        # Check if already packed by trying to get pack_info
                        self.classification_frame.pack_info()
                        DEBUG("classification_frame already shown")
                    except tk.TclError:
                        # Not packed, so pack it
                        self.classification_frame.pack(before=self.bottom_frame, side="top", anchor="center")
                        DEBUG("classification_frame shown")
                    
            else:
                # If we want to hide the classification_frame
                if hasattr(self, 'classification_frame') and self.classification_frame is not None:
                    try:
                        # Check if packed by trying to get pack_info
                        self.classification_frame.pack_info()
                        # If we reach here, it's packed, so hide it
                        self.classification_frame.pack_forget()
                        DEBUG("classification_frame hidden")
                    except tk.TclError:
                        # Not packed, nothing to hide
                        DEBUG("classification_frame was already hidden")
        except Exception as e:
            operation = "show" if show else "hide"
            frame_exists = hasattr(self, 'classification_frame') and self.classification_frame is not None
            ERROR("Error toggling classification frame (operation: {}, frame_exists: {}, error: {})", 
                  operation, frame_exists, e)
            # Try to provide more context for debugging
            if hasattr(self, 'classification_frame') and self.classification_frame is not None:
                try:
                    widget_info = self.classification_frame.winfo_exists()
                    DEBUG("Frame widget exists: {}", widget_info)
                except:
                    DEBUG("Frame widget state unknown")

    def toggle_cut_image(self, show):
        """Toggle cut image feature visibility"""
        try:
            if show is True:
                # If we want to show but cut_frame doesn't exist, create it
                if not hasattr(self, 'cut_frame') or self.cut_frame is None:
                    DEBUG("Creating cut image frame for show operation")
                    self.create_cut_image_bt()
                else:
                    try:
                        # Check if already packed by trying to get pack_info
                        self.cut_frame.pack_info()
                    except tk.TclError:
                        # Not packed, so pack it
                        self.cut_frame.pack(side="top", anchor="center")
                        DEBUG("cut_frame shown")
                
                # Create vertical line if there's an image on canvas
                if hasattr(self, 'canvas') and self.canvas is not None:
                    self.create_vertical_line()
                
                # Bind keyboard shortcut if not already bound
                if not hasattr(self, '_cut_image_bound') or not self._cut_image_bound:
                    self.window.bind("<Shift-C>", self.cut_image)
                    self._cut_image_bound = True
                        
            else:
                # If we want to hide the cut_frame
                if hasattr(self, 'cut_frame') and self.cut_frame is not None:
                    try:
                        # Check if packed by trying to get pack_info
                        self.cut_frame.pack_info()
                        self.cut_frame.pack_forget()
                        DEBUG("cut_frame hidden")
                    except tk.TclError:
                        # Already not packed
                        pass
                
                # Hide vertical line by removing it
                if hasattr(self, 'cut_line') and self.cut_line is not None:
                    # Remove the line elements from canvas
                    try:
                        if hasattr(self.cut_line, 'bg_line'):
                            self.canvas.delete(self.cut_line.bg_line)
                        if hasattr(self.cut_line, 'fg_line'):
                            self.canvas.delete(self.cut_line.fg_line)
                        self.cut_line = None
                        DEBUG("Vertical cut line removed")
                    except Exception as line_error:
                        ERROR("Error removing vertical line: {}", line_error)
                
                # Unbind keyboard shortcut
                if hasattr(self, '_cut_image_bound') and self._cut_image_bound:
                    self.window.unbind("<Shift-C>")
                    self._cut_image_bound = False
                    
        except Exception as e:
            ERROR("Error toggling cut image feature: {}", e)
            
            
    def next_image(self, event):
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        DEBUG("next_image")
        if self.dispatch:
            self.dispatch(UIEvent.NEXT_IMAGE, {"value": event})

    def previous_image(self, event):
        if self.input_box and self.window.focus_get() is self.input_box:
            return

        DEBUG("previous_image")
        if self.dispatch:
            self.dispatch(UIEvent.PREVIOUS_IMAGE, {"value": event})

    # Bind key and mouse with events
    def setup_events(self):
        # Store current hotkey bindings for rebinding
        self.hotkey_bindings = {}

        # Bind configurable hotkeys
        self.bind_configurable_hotkeys()

        # Bind non-configurable events
        # Right Ctrl key release (companion to Control_L)
        self.window.bind("<Control_R>", self.on_rc_press)
        self.window.bind("<KeyRelease-Control_R>", self.on_rc_release)

        # Windows changes position or size
        self.window.bind("<Configure>", self.on_win_configure)

        # Clear focus on window click
        self.window.bind("<Button-1>", self._clear_focus)

        # Mouse event binding (support drawing functionality)
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<Button-3>", self.on_mouse_click_right)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def bind_configurable_hotkeys(self):
        """Bind hotkeys from configuration"""
        # Get hotkeys from config
        hotkeys = config_utils.get_all_hotkeys()

        # Map action keys to handler methods
        action_handlers = {
            'previous_image': self.previous_image,
            'next_image': self.next_image,
            'toggle_drawing_mode': self.toggle_drawing_mode,
            'delete_bbox': self.delete_bbox,
            'search_file': self.search_file,
            'quick_correct': self.quick_correct,
            'cut_image': self.cut_image,
            'delete_image': self.delete_image,
        }

        # Bind each hotkey to its handler
        for action_key, hotkey in hotkeys.items():
            # Only bind if hotkey is not empty (skip empty or whitespace-only strings)
            if action_key in action_handlers and hotkey and hotkey.strip():
                handler = action_handlers[action_key]
                try:
                    self.window.bind(hotkey, handler)

                    # For single letter keys without modifiers, also bind uppercase
                    if hotkey.startswith('<') and hotkey.endswith('>'):
                        key = hotkey[1:-1]  # Remove < and >
                        # Check if it's a single letter without modifiers (no dash)
                        if len(key) == 1 and key.isalpha() and '-' not in hotkey:
                            self.window.bind(f'<{key.upper()}>', handler)
                            DEBUG(f"Also bound uppercase variant <{key.upper()}> for {action_key}")

                    # Store binding for later unbinding
                    self.hotkey_bindings[action_key] = hotkey

                    DEBUG(f"Bound hotkey {hotkey} to {action_key}")
                except tk.TclError as e:
                    ERROR(f"Failed to bind hotkey {hotkey} for {action_key}: {e}")

    def rebind_hotkeys(self):
        """Unbind old hotkeys and rebind with new configuration"""
        # Unbind old hotkeys
        for action_key, old_hotkey in self.hotkey_bindings.items():
            # Only unbind if hotkey is not empty
            if old_hotkey and old_hotkey.strip():
                try:
                    self.window.unbind(old_hotkey)

                    # Also unbind uppercase variant for single letter keys without modifiers
                    if old_hotkey.startswith('<') and old_hotkey.endswith('>'):
                        key = old_hotkey[1:-1]
                        # Check if it's a single letter without modifiers (no dash)
                        if len(key) == 1 and key.isalpha() and '-' not in old_hotkey:
                            self.window.unbind(f'<{key.upper()}>')
                except tk.TclError:
                    # Ignore errors when unbinding non-existent bindings
                    DEBUG(f"Failed to unbind hotkey {old_hotkey} for {action_key}")

        # Clear old bindings
        self.hotkey_bindings.clear()

        # Bind new hotkeys
        self.bind_configurable_hotkeys()

        INFO("Hotkeys rebound successfully")
        

    def select_folder(self, title):
        folder_path = filedialog.askdirectory(parent = self.window, title = title)
        return folder_path

    def show_info(self, msg):
        messagebox.showinfo("info", str(msg))
        
    def show_warning(self, msg):
        messagebox.showwarning("Error", str(msg))
        
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
        if self.dispatch:
            self.dispatch(UIEvent.DELETE_BBOX, {"value": None})
    
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

    def update_tilt_angle_display(self, angle=None, iou=None):
        """
        Update tilt angle and IoU display with independent color coding

        Args:
            angle (float): Tilt angle in degrees, None if no angle available
            iou (float): Average IoU value (0.0 to 1.0), None if no IoU available
        """
        if not self.SHOW_TILT_ANGLE:
            self.tilt_angle_label.config(text="")
            self.iou_label.config(text="")
            return

        # === Update tilt angle label ===
        if angle is None:
            angle_text = "N/A"
            angle_color = "#8E8E79"  # Gray for N/A
        else:
            # Format angle with sign
            if angle >= 0:
                angle_text = f"+{angle:.1f}°"
            else:
                angle_text = f"{angle:.1f}°"

            # Color coding based on angle magnitude
            abs_angle = abs(angle)
            if abs_angle < 2.0:
                angle_color = "#00AA00"  # Green for good alignment
            elif abs_angle < 5.0:
                angle_color = "#FFA500"  # Orange for slight tilt
            else:
                angle_color = "#C00C0C"  # Red for significant tilt

        self.tilt_angle_label.config(text=angle_text, fg=angle_color)

        # === Update IoU label ===
        if iou is None:
            iou_text = "IoU: N/A"
            iou_color = "#8E8E79"  # Gray for N/A
        else:
            iou_text = f"IoU: {iou:.2f}"

            # Color coding based on IoU value
            if iou < 0.1:
                iou_color = "#00AA00"  # Green for good spacing
            elif iou < 0.3:
                iou_color = "#FFA500"  # Orange for slight overlap
            else:
                iou_color = "#C00C0C"  # Red for significant overlap

        self.iou_label.config(text=iou_text, fg=iou_color)

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

    def _clear_focus(self, event):
        if event.widget not in (self.input_box, self.label_text_box, self.index_entry):
            self.window.focus_set()

    def run(self):
        if self.dispatch:
            self.window.after_idle(lambda: self.dispatch(UIEvent.WINDOW_READY, {}))
        self.window.mainloop()


# for implementation testing
if __name__ == "__main__":
    ui = UI()
    ui.run()
