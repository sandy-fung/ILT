import tkinter as tk
from tkinter import filedialog
from UI_event import UIEvent
from log_levels import DEBUG, INFO, ERROR
from tkinter import messagebox
import label_display_utils
import bbox_controller

class UI:
    def __init__(self):
        self.dispatch = None
        self.window_width = 1920
        self.window_height = 1080

        # Create the main window
        self.window = tk.Tk()
        self.window.title("Image Labelling Tool")
        self.window.geometry(f"{self.window_width}x{self.window_height}")
        
        # Ensure window can receive keyboard focus
        self.window.focus_set()
        self.window.focus_force()

        # Initialize drawing-related states
        self.ctrl_pressed = False
        self.drawing_mode = False
        self.bbox_controller = None

        self.SHOW_CLASS_ID_BUTTONS = False
        self.SHOW_TEXT_BOX = False

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
        
        # Initialize drawing controller
        self.bbox_controller = bbox_controller.BBoxController(self.canvas)

        # Create context menu (reuse approach from image_label_tool)
        self.create_context_menu()

    def create_canvas(self):
        self.canvas_frame = tk.Frame(self.middle_frame)
        self.canvas_frame.pack(side = "left", fill = "both", expand = True)
        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness = 0)
        self.canvas.pack(fill = "both", expand = True)


    def create_bottom_area(self):
        self.bottom_frame = tk.Frame(self.window, relief = "ridge", bd = 2)
        self.bottom_frame.pack(side = "bottom", fill = "x")

        self.create_text_area()
        self.create_hint_area()

    def create_text_area(self):
        self.text_frame = tk.Frame(self.bottom_frame, bg = "#f8f8f8")
        self.text_frame.pack(side = "left", fill = "both", expand = True)

        if not self.SHOW_TEXT_BOX:
            DEBUG("Text box is not shown as per configuration.")
            return
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
            "拖曳選中的box：移動box位置\n"
            "滑鼠右鍵：刪除選中的box\n"
            "Delete鍵：刪除選中的box\n"
            "Ctrl：切換繪框模式\n"
            "繪框模式下拖拽：繪製新box"
            )
        self.hint_label = tk.Label(
            self.hint_frame,
            width = 50, height = 10, bg = "#f8f8f8",
            text = hint_text, justify = "left", anchor = "w", fg = "#424242", font = ("Segoe UI", 11)
        ) 
        self.hint_label.grid(row = 1, column = 0, columnspan = 2, sticky = "s", padx = 20)
        self.index_label = tk.Label(self.hint_frame, bg = "#f8f8f8", text = " : ", fg = "#829901", font = ("Segoe UI", 11))
        self.index_label.grid(row = 0, column = 2, sticky = "nwse")


    # Add drawing mode status display
        self.drawing_mode_label = tk.Label(
            self.hint_frame, bg = "#f8f8f8", text = "普通模式", 
            fg = "#424242", font = ("Segoe UI", 11, "bold")
        )
        self.drawing_mode_label.grid(row = 0, column = 0, sticky = "nw", padx = 20)
        
        # Add selection status display
        self.selection_status_label = tk.Label(
            self.hint_frame, bg = "#f8f8f8", text = "未選中任何框", 
            fg = "#666666", font = ("Segoe UI", 10)
        )
        self.selection_status_label.grid(row = 0, column = 1, sticky = "nw", padx = (20, 0))

    def show_class_id_buttons(self, var, labels):
        if self.SHOW_CLASS_ID_BUTTONS:
            DEBUG("show_class_id_buttons with var: {}, labels: {}", var, labels)
            self.class_id_frame = tk.Frame(self.middle_frame, bg = "#f8f8f8")
            self.class_id_frame.pack(side = "right", fill = "y")

            self.class_id_vars = tk.StringVar(value = var)
            for i, label in enumerate(labels):
                column = i // 13
                row = i % 13
                button = tk.Radiobutton(
                    self.class_id_frame, bg = "#f8f8f8", font = ("Segoe UI Mono", 10),
                    text = label, variable = self.class_id_vars, value = label, width = 3, anchor = "center", indicatoron = True,
                    command = lambda l = label: self.dispatch(UIEvent.CLASS_ID_CHANGE, {"label": l})
             ) if self.dispatch else None
                button.grid(row = row, column = column, padx = 5, pady = 5)

        else:
            return
        

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
        if self.dispatch:
            self.dispatch(UIEvent.CANVAS_RESIZE, {})

    def update_image_canvas(self, image):
        DEBUG("update_image_canvas")
        self.canvas.delete("all")
        self.canvas.image = image
        self.canvas.create_image(self.canvas_width//2, self.canvas_height//2, anchor = "center", image = image)
        DEBUG("Image updated on canvas with height: {}, width: {}", self.canvas_height, self.canvas_width)

    def draw_labels_on_canvas(self, labels):
        """Draw label bounding boxes on canvas (完全複用 image_label_tool 的清除機制避免殘影)"""
        # Clear ALL previous label-related items to avoid 殘影 (複用 image_label_tool 的完整清除策略)
        # 使用更廣泛的標籤清除，確保不會有任何殘影
        self.canvas.delete("label_box")
        self.canvas.delete("label_box_selected")
        self.canvas.delete("label_box_dragging") 
        self.canvas.delete("label_text")
        
        # 額外清除任何可能的殘留項目 (加強版清除機制)
        for item in self.canvas.find_withtag("label_box"):
            self.canvas.delete(item)
        for item in self.canvas.find_withtag("label_box_selected"):
            self.canvas.delete(item)
        for item in self.canvas.find_withtag("label_box_dragging"):
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
            
            # Determine color and style based on state (複用 image_label_tool 的視覺回饋邏輯)
            if self.bbox_controller and self.bbox_controller.is_dragging and label == self.bbox_controller.dragging_label:
                # Dragging: special style with dashed line and bright color
                color = "#00FFFF"  # Cyan for dragging
                width = 4
                tags = "label_box_dragging"
                dash = (5, 5)  # Dashed line pattern
            elif hasattr(label, 'selected') and label.selected:
                # Selected: red color with thicker border
                color = "#FF0000"  # Red
                width = 3
                tags = "label_box_selected"
                dash = None
            else:
                # Not selected: original color based on class_id
                color = colors[label.class_id % len(colors)]
                width = 2
                tags = "label_box"
                dash = None
            
            # Draw bounding box (複用 image_label_tool 的樣式設定)
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
            
            # Draw class ID text
            text_x = x1
            text_y = y1 - 5 if y1 > 15 else y2 + 5
            
            self.canvas.create_text(
                text_x, text_y,
                text=str(label.class_id),
                fill=color,
                anchor="nw",
                font=("Arial", 10, "bold"),
                tags="label_text"
            )
            
            DEBUG("Drew label: class_id={}, coords=({:.1f},{:.1f},{:.1f},{:.1f})", 
                  label.class_id, x1, y1, x2, y2)

# Update text and index labels
    def update_text_box(self, content):
        if not self.SHOW_TEXT_BOX:
            DEBUG("Text box is not shown as per configuration.")
            return
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
        """Handle mouse press event - support drawing and dragging modes (複用 image_label_tool 的模式)"""
        DEBUG("on_mouse_press at ({}, {})", event.x, event.y)
        
        if self.bbox_controller and self.bbox_controller.is_in_drawing_mode():
            # Drawing mode: start drawing
            if self.bbox_controller.start_drawing(event.x, event.y):
                if self.dispatch:
                    self.dispatch(UIEvent.MOUSE_LEFT_PRESS, {"value": event})
                return
        
        # Normal mode: handle selection and dragging
        if self.dispatch:
            self.dispatch(UIEvent.MOUSE_LEFT_PRESS, {"value": event, "x": event.x, "y": event.y})
    
    def on_mouse_release(self, event):
        """Handle mouse release event - support drawing and dragging modes (複用 image_label_tool 的模式)"""
        DEBUG("on_mouse_release at ({}, {})", event.x, event.y)
        
        if self.bbox_controller and self.bbox_controller.is_in_drawing_mode():
            # Drawing mode: complete drawing
            drawing_result = self.bbox_controller.finish_drawing(event.x, event.y)
            if drawing_result and self.dispatch:
                self.dispatch(UIEvent.MOUSE_LEFT_RELEASE, {"value": event, "drawing_result": drawing_result})
        elif self.bbox_controller and self.bbox_controller.is_dragging:
            # Dragging mode: complete dragging
            dragged_label = self.bbox_controller.finish_drag()
            if dragged_label and self.dispatch:
                self.dispatch(UIEvent.MOUSE_LEFT_RELEASE, {"value": event, "dragged_label": dragged_label})
        
    def on_mouse_drag(self, event):
        """Handle mouse drag event - drawing preview and dragging (複用 image_label_tool 的模式)"""
        if self.bbox_controller and self.bbox_controller.is_in_drawing_mode():
            # Drawing mode: update preview
            self.bbox_controller.update_preview(event.x, event.y)
            if self.dispatch:
                self.dispatch(UIEvent.MOUSE_DRAG, {"value": event})
        elif self.bbox_controller and self.bbox_controller.is_dragging:
            # Dragging mode: update drag position
            self.bbox_controller.update_drag(event.x, event.y)
            if self.dispatch:
                self.dispatch(UIEvent.MOUSE_DRAG, {"value": event, "x": event.x, "y": event.y})

    # Key events
    def on_lc_press_switch_pen(self, event):
        """Left Ctrl key toggle drawing mode"""
        DEBUG("on_lc_press_switch_pen triggered")
        
        self.ctrl_pressed = not self.ctrl_pressed
        
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
        self.ctrl_pressed = True
        DEBUG("Ron_rc_press")
        if self.dispatch:
            self.dispatch(UIEvent.RIGHT_CTRL_PRESS, {"value": event})

    def on_rc_release(self, event):
        self.ctrl_pressed = False
        DEBUG("on_rc_release")
        if self.dispatch:
            self.dispatch(UIEvent.RIGHT_CTRL_RELEASE, {"value": event})

    def on_delete_key(self, event):
        DEBUG("on_delete_key")
        if self.dispatch:
            self.dispatch(UIEvent.DELETE_KEY, {"value": event})

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
        """創建右鍵選單 (複用 image_label_tool 的方法)"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="刪除", command=self.delete_from_context_menu)
    
    def show_context_menu(self, event):
        """顯示右鍵菜單 (複用 image_label_tool 的座標方式)"""
        try:
            # 使用參考專案的座標轉換方式
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def delete_from_context_menu(self):
        """從右鍵菜單觸發刪除 (複用 image_label_tool 的確認邏輯)"""
        # 顯示確認對話框 (參考 plate_box_3.py 的實現)
        result = messagebox.askyesno("Delete", "Delete selected box?")
        if result and self.dispatch:
            self.dispatch(UIEvent.DELETE_KEY, {"value": None})

    # Drawing mode related methods
    def get_drawing_mode(self):
        """Get current drawing mode status"""
        return self.drawing_mode
    
    def set_drawing_mode(self, mode):
        """Set drawing mode"""
        if self.bbox_controller:
            self.bbox_controller.set_drawing_mode(mode)
            self.drawing_mode = mode
            self.update_drawing_mode_display()
            DEBUG("Drawing mode set to: {}", mode)
    
    def cancel_current_drawing(self):
        """Cancel current drawing"""
        if self.bbox_controller:
            self.bbox_controller.cancel_drawing()
    
    def update_drawing_mode_display(self):
        """Update drawing mode status display"""
        if self.drawing_mode:
            self.drawing_mode_label.config(text="繪框模式", fg="#FF6B35")
        else:
            self.drawing_mode_label.config(text="普通模式", fg="#424242")
    
    def update_selection_status_display(self, selected_label=None):
        """Update selection status display (複用 image_label_tool 的狀態顯示邏輯)"""
        if self.bbox_controller and self.bbox_controller.is_dragging:
            # 拖曳模式顯示
            dragging_label = self.bbox_controller.dragging_label
            status_text = f"拖曳中：class_id={dragging_label.class_id}"
            self.selection_status_label.config(text=status_text, fg="#00FFFF")
        elif selected_label:
            status_text = f"已選中：class_id={selected_label.class_id}"
            self.selection_status_label.config(text=status_text, fg="#FF0000")
        else:
            self.selection_status_label.config(text="未選中任何框", fg="#666666")
    
    def update_dragging_status_display(self, is_dragging=False, dragged_label=None):
        """
        更新拖曳狀態顯示 (複用 image_label_tool 的狀態回饋邏輯)
        
        Args:
            is_dragging (bool): 是否正在拖曳
            dragged_label (LabelObject): 被拖曳的標籤對象
        """
        if is_dragging and dragged_label:
            status_text = f"拖曳中：class_id={dragged_label.class_id}, 座標=({dragged_label.cx_ratio:.3f}, {dragged_label.cy_ratio:.3f})"
            self.selection_status_label.config(text=status_text, fg="#00FFFF")
        else:
            # 恢復選擇狀態顯示
            self.update_selection_status_display(self.bbox_controller.get_selected_label() if self.bbox_controller else None)

    def run(self):
        if self.dispatch:
            self.window.after_idle(lambda: self.dispatch(UIEvent.WINDOW_READY, {}))
        self.window.mainloop()