import tkinter as tk

window_width = 1920
window_height = 1080

# Create the main window
window = tk.Tk()
window.title("ILT UI")
window.geometry(f"{window_width}x{window_height}")

#上半的圖片
image_frame = tk.Frame(window, bg = "black")
image_frame.pack(side = "top", fill = "both", expand = True)
canvas = tk.Canvas(image_frame, bg = "black")
canvas.pack(fill = "both", expand = True)

#下半區
bottom_frame = tk.Frame(window, bg = "gray")
bottom_frame.pack(side = "bottom", fill = "both", expand = True)

text_frame = tk.Frame(bottom_frame, bg = "white")
text_frame.pack(side = "left", fill = "both", expand = True)
text_label = tk.Label(text_frame, text = "This is the text area", bg = "gray", relief = "sunken" ) #label的顯示區
text_label.pack(side = "top", fill = "both", expand = True, padx = 20, pady = 20)
reselect_button = tk.Button(text_frame, width = 16, height = 1, text = "Reselect folders", bg = "lightgray", bd = 2, relief = "raised")
reselect_button.pack(side = "bottom")

hint_frame = tk.Frame(bottom_frame, bg = "gray")
hint_frame.pack(side = "right", fill = "both", expand = True)

hint_text = (
    "← 上一張\n"
    "→ 下一張\n"
    "滑鼠左鍵：選取box\n"
    "滑鼠右鍵：刪除box\n"
    "Ctrl + 滑鼠左鍵：繪製box")
hint_label = tk.Label(hint_frame, text = hint_text, justify = "left") #hint的顯示區
hint_label.grid(row = 0, column = 0, columnspan = 2, sticky = "s",  padx = 20, pady = 20)
crop_button = tk.Button(hint_frame, width = 4, height = 1, text = "Crop", bg = "lightgray", bd = 2, relief = "raised")
crop_button.grid(row = 2, column = 0, sticky = "s")
add_button = tk.Button(hint_frame, width = 4, height = 1, text = "Add", bg = "lightgray", bd = 2, relief = "raised")
add_button.grid(row = 2, column = 1, sticky = "s")

window.mainloop()