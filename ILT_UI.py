import tkinter as tk

class Initial:
    def __init__(self):
        self.window_width = 1920
        self.window_height = 1080

        # Create the main window
        self.window = tk.Tk()
        self.window.title("ILT UI")
        self.window.geometry(f"{self.window_width}x{self.window_height}")

        self.setup_ui()
        self.setup_events()
        self.ctrl_pressed = False

        self.window.mainloop()
    
    def setup_ui(self):
        self.create_top_area()
        self.create_bottom_area()

    def create_top_area(self):
        self.image_frame = tk.Frame(self.window, bg = "black")
        self.image_frame.pack(side = "top", fill = "both", expand = True)
        self.canvas = tk.Canvas(self.image_frame, bg = "black")
        self.canvas.pack(fill = "both", expand = True)

    def create_bottom_area(self): 
        self.bottom_frame = tk.Frame(self.window, bg = "gray")
        self.bottom_frame.pack(side = "bottom", fill = "both", expand = True)

        self.create_text_area()
        self.create_hint_area()    

    def create_text_area(self):
        self.text_frame = tk.Frame(self.bottom_frame, bg = "white")
        self.text_frame.pack(side = "left", fill = "both", expand = True)
        
        self.text_label = tk.Label(self.text_frame, text = "This is the text area", bg = "gray", relief = "sunken")
        self.text_label.pack(side = "top", fill = "both", ecpand = True, padx = 20, pady = 20)
        self.reselect_button = tk.Button(self.text_frame, width = 16, height = 1, text = "Reselect folders", bg = "lightgray", bd = 2, relief = "raised", command = self.on_bt_click_reselect)
        self.reselect_button.pack(side = "bottom") 
        
    def create_hint_area(self):  
        self.hint_frame = tk.Frame(self.bottom_frame, bg = "gray")
        self.hint_frame.pack(side = "right", fill = "both", expand = True)            

        hint_text = (
            "← 上一張\n"
            "→ 下一張\n"
            "滑鼠左鍵：選取box\n"
            "滑鼠右鍵：刪除box\n"
            "Ctrl + 滑鼠左鍵：繪製box"
            )
        self.hint_label = tk.Label(self.hint_frame, text = hint_text, justify = "left") #hint的顯示區
        self.hint_label.grid(row = 0, column = 0, columnspan = 2, sticky = "s",  padx = 20, pady = 20)
        self.crop_button = tk.Button(self.hint_frame, width = 4, height = 1, text = "Crop", bg = "lightgray", bd = 2, relief = "raised", command = self.on_bt_click_crop)
        self.crop_button.grid(row = 2, column = 0, sticky = "s")
        self.add_button = tk.Button(self.hint_frame, width = 4, height = 1, text = "Add", bg = "lightgray", bd = 2, relief = "raised", command = self.on_bt_click_add)
        self.add_button.grid(row = 2, column = 1, sticky = "s")

    def update_text_label(self, text):
        self.text_label.config(text = text)

    # Button events
    def on_bt_click_reselect(self):
        print("on_bt_click_reselect")
        self.dispatch(UIEvent.RESELECT_BT_CLICK)
    def on_bt_click_crop(self):
        print("on_bt_click_crop")
        self.dispatch(UIEvent.CROP_BT_CLICK)
    
    def on_bt_click_add(self):
        print("on_bt_click_add")
        self.dispatch(UIEvent.ADD_BT_CLICK)

    # Mouse events
    def on_mouse_click_right(self, event):
        print("on_mouse_click_right")

    def on_mouse_click_left(self, event):
        print("on_mouse_click_left")

    # Key events 
    def on_lc_press_switch_pen(self, event):
        self.ctrl_pressed = not self.ctrl_pressed
        print("Left crtl is pressed.)")
    
    def on_rc_press(self, event):
        self.ctrl_pressed = Truee
        print("Right crtl is being pressed.")

    def on_rc_release(self, event):
        self.ctrl_pressed = False
        print("Ringht ctrl is released.")

    def next_image(self, event):
        print("Next image")
    
    def previous_image(self, event):
        print("Previous image")
    
    # Bind key and mouse with events
    def setup_events(self):
        self.window.bind("<Left>", self.previous_image)
        self.window.bind("<Right>", self.next_image)
        self.window.bind("<Control_L>", self.on_lc_press_switch_pen)
        self.window.bind("<Control_R>", self.on_rc_press)
        self.window.bind("<KeyRelease-Control_R>", self.on_rc_release)

        self.canvas.bind("<Button--1>", self.on_mouse_click_left)
        self.canvas.bind("<Button-3>", self.on_mouse_click_right)