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
text_label = tk.Label(text_frame, text = "This is the text area", bg = "gray") #label的顯示區
text_label.pack(side = "top", fill = "y", expand = True)
reselect_button = tk.Button(text_frame, width = 16, height = 1, text = "Reselect folders", bg = "lightgray", bd = 2, relief = "raised")
reselect_button.pack(side = "bottom")


hint_frame = tk.Frame(bottom_frame, bg = "gray")
hint_frame.pack(side = "right", fill = "both", expand = True)
hint_label = tk.Label(hint_frame, text = "This is the hint area", bg = "white") #hint的顯示區
hint_label.grid(row = 0, column = 1, sticky = "se", padx = 10, pady = 10)
crop_button = tk.Button(hint_frame, width = 4, height = 1, text = "Crop", bg = "lightgray", bd = 2, relief = "raised")
crop_button.grid(row = 1, column = 0, sticky = "se", padx = 10, pady = 10)
add_button = tk.Button(hint_frame, width = 3, height = 1, text = "Add", bg = "lightgray", bd = 2, relief = "raised")
add_button.grid(row = 1, column = 1, sticky = "se", padx = 10, pady = 10)

window.mainloop()