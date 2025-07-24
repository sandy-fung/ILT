import tkinter as tk

def draw_outlined_text(canvas, x, y, text, font, outline_color="white", fill_color="black", thickness=2, tags=""):
    # 在周圍畫出 8 個白色文字當作邊框
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            canvas.create_text(x + dx, y + dy, text=text, font=font, fill=outline_color,tags=tags)

    # 正中央黑字
    canvas.create_text(x, y, text=text, font=font, fill=fill_color,tags=tags)

if __name__ == "__main__":
    root = tk.Tk()
    canvas = tk.Canvas(root, width=400, height=200, bg="gray")
    canvas.pack()

    draw_outlined_text(canvas, 200, 100, "黑字白邊", font=("Arial", 40, "bold"), outline_color="white", fill_color="black", thickness=2)

    root.mainloop()
