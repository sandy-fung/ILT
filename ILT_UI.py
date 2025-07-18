import tkinter as tk
from tkinter import filedialog
from UI_event import UIEvent
from log_levels import DEBUG, INFO, ERROR
from tkinter import messagebox

class UI:
    def __init__(self):
        self.dispatch = None
        self.window_width = 1920
        self.window_height = 1080

        # Create the main window
        self.window = tk.Tk()
        self.window.title("Image Labelling Tool")
        self.window.geometry(f"{self.window_width}x{self.window_height}")

        self.setup_ui()
        self.setup_events()
        self.ctrl_pressed = False

    def set_dispatcher(self, event_dispatcher):
        self.dispatch = event_dispatcher

# Define UI components
    def setup_ui(self):
        self.create_top_area()
        self.create_middle_area()
        self.create_bottom_area()

    def create_top_area(self):
        self.toolbar =  tk.Frame(self.window)
        self.toolbar.pack(side = "top", fill = "x")

        self.reselect_button = tk.Button(
            self.toolbar,
            width = 16, height = 1,
            text = "Reselect Folders", fg = "#008378",
            relief = "flat", bd = 2,
            command = self.on_bt_click_reselect
        )
        self.reselect_button.pack(side = "left", padx = 5)
        
        self.crop_button = tk.Button(
            self.toolbar,
            width = 4, height = 1,
            text = "Crop", fg = "#008378",
            relief = "flat", bd = 2,
            command = self.on_bt_click_crop
        )
        self.crop_button.pack(side = "left")
        
        self.add_button = tk.Button(
            self.toolbar,
            width = 4, height = 1,
            text = "Add", fg = "#008378", 
            relief = "flat", bd = 2,
            command = self.on_bt_click_add
        )
        self.add_button.pack(side = "left", padx = 5)

    def create_middle_area(self):
        self.middle_frame = tk.Frame(self.window)
        self.middle_frame.pack(side = "top", fill = "both", expand = True)

        self.create_canvas()
        self.create_class_id_area()

    def create_canvas(self):
        self.canvas_frame = tk.Frame(self.middle_frame)
        self.canvas_frame.pack(side = "left", fill = "both", expand = True)
        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness = 0)
        self.canvas.pack(fill = "both", expand = True)

    def create_class_id_area(self):
        self.class_id_frame = tk.Frame(self.middle_frame)
        self.class_id_frame.pack(side = "right", fill = "y")

    def create_bottom_area(self):
        self.bottom_frame = tk.Frame(self.window, relief = "ridge", bd = 2)
        self.bottom_frame.pack(side = "bottom", fill = "x")

        self.create_text_area()
        self.create_hint_area()

    def create_text_area(self):
        self.text_frame = tk.Frame(self.bottom_frame, bg = "#f8f8f8")
        self.text_frame.pack(side = "left", fill = "both", expand = True)

        self.text_box = tk.Text(
            self.text_frame,
            height = 15, bg = "white",
            font = ("Segoe UI", 11), fg = "#424242",
            relief = "sunken",
            wrap = "word"
        )
        self.text_box.tag_configure("left", justify = "left")
        self.text_box.pack(side = "top", fill = "x", padx = 20, pady = 20)

    def create_hint_area(self):
        self.hint_frame = tk.Frame(self.bottom_frame, bg = "#f8f8f8")
        self.hint_frame.pack(side = "right", fill = "both", expand = True)

        hint_text = (
            "← 上一張\n"
            "→ 下一張\n"
            "滑鼠左鍵：選取box\n"
            "滑鼠右鍵：刪除box\n"
            "Ctrl + 滑鼠左鍵：繪製box"
            )
        self.hint_label = tk.Label(
            self.hint_frame,
            width = 50, height = 10, bg = "#f8f8f8",
            text = hint_text, justify = "left", anchor = "w", fg = "#424242", font = ("Segoe UI", 11)
        ) 
        self.hint_label.grid(row = 1, column = 0, columnspan = 2, sticky = "s", padx = 20)
        self.index_label = tk.Label(self.hint_frame, bg = "#f8f8f8", text = " : ", fg = "#829901", font = ("Segoe UI", 11))
        self.index_label.grid(row = 0, column = 2, sticky = "nwse")

# Draw class id buttons
    def draw_class_id_buttons(self, var, labels):
        self.class_id_vars = tk.StringVar(value = var)
        for i, label in enumerate(labels):
            column = i // 13
            row = i % 13
            button = tk.Radiobutton(self.class_id_frame, text = label, variable = self.class_id_vars, value = label, command = lambda l = label: self.dispatch(UIEvent.CLASS_ID_CHANGE, {"label": l}))
            button.grid(row = row, column = column, sticky = "e", padx = 5, pady = 5)

# About canvas
    def get_canvas_size(self):
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        DEBUG("Canvas size: height: {}, width: {}", self.canvas_height, self.canvas_width)
        if self.canvas_height == 0 or self.canvas_width == 0:
            self.canvas_height = 720
            self.canvas_width = 1920
        return self.canvas_height, self.canvas_width
    
    def on_canvas_resize(self, event):
        self.dispatch(UIEvent.CANVAS_RESIZE, {})

    def update_image_canvas(self, image):
        DEBUG("update_image_canvas")
        self.canvas.delete("all")
        self.canvas.image = image
        self.canvas.create_image(self.canvas_width//2, self.canvas_height//2, anchor = "center", image = image)
        DEBUG("Image updated on canvas with height: {}, width: {}", self.canvas_height, self.canvas_width)

# Update text and index labels
    def update_text_box(self, content):
        self.text_box.config(state = "normal")
        self.text_box.delete("1.0", tk.END) # Clear the text box
        self.text_box.insert(tk.END, content)

    def update_index_label(self, index, path):
        DEBUG("update_index_label")
        self.index_label.config(text = f"{index + 1} : {len(path)}")
        DEBUG("Index label updated with index: {}", index)


# Button events
    def on_bt_click_reselect(self):
        DEBUG("on_bt_click_reselect")
        self.dispatch(UIEvent.RESELECT_BT_CLICK, {})

    def on_bt_click_crop(self):
        DEBUG("on_bt_click_crop")
        self.dispatch(UIEvent.CROP_BT_CLICK, {})

    def on_bt_click_add(self):
        DEBUG("on_bt_click_add")
        self.dispatch(UIEvent.ADD_BT_CLICK, {})        

    # Mouse events
    def on_mouse_click_right(self, event):
        DEBUG("on_mouse_click_right")
        self.dispatch(UIEvent.MOUSE_RIGHT_CLICK, {"value": event})

    def on_mouse_click_left(self, event):
        DEBUG("on_mouse_click_left")
        self.dispatch(UIEvent.MOUSE_LEFT_CLICK, {"value": event})

    # Key events
    def on_lc_press_switch_pen(self, event):
        self.ctrl_pressed = not self.ctrl_pressed
        DEBUG("on_lc_press_switch_pen")
        self.dispatch(UIEvent.LEFT_CTRL_PRESS, {"value": event})

    def on_rc_press(self, event):
        self.ctrl_pressed = True
        DEBUG("Ron_rc_press")
        self.dispatch(UIEvent.RIGHT_CTRL_PRESS, {"value": event})

    def on_rc_release(self, event):
        self.ctrl_pressed = False
        DEBUG("on_rc_release")
        self.dispatch(UIEvent.RIGHT_CTRL_RELEASE, {"value": event})


    def next_image(self, event):
        DEBUG("next_image")
        self.dispatch(UIEvent.RIGHT_PRESS, {"value": event})

    def previous_image(self, event):
        DEBUG("previous_image")
        self.dispatch(UIEvent.LEFT_PRESS, {"value": event})

    # Bind key and mouse with events
    def setup_events(self):
        self.window.bind("<Left>", self.previous_image)
        self.window.bind("<Right>", self.next_image)
        self.window.bind("<Control_L>", self.on_lc_press_switch_pen)
        self.window.bind("<Control_R>", self.on_rc_press)
        self.window.bind("<KeyRelease-Control_R>", self.on_rc_release)

        self.canvas.bind("<Button--1>", self.on_mouse_click_left)
        self.canvas.bind("<Button-3>", self.on_mouse_click_right)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def select_folder(self, title):
        folder_path = filedialog.askdirectory(parent = self.window, title = title)
        return folder_path

    def show_error(self, msg):
        messagebox.showerror("Error", str(msg))


    def run(self):
        self.window.after_idle(lambda: self.dispatch(UIEvent.WINDOW_READY, {}))
        self.window.mainloop()