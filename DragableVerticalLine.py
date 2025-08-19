import tkinter as tk

class DraggableVerticalLine:
    def __init__(
        self,
        canvas: tk.Canvas,
        x: int = 100,
        foreground: str = "#222",
        background: str = "#ddd",
        width_fg: int = 2,
        width_bg: int = 6,
        grab_px: int = 6,
        bounds=None,
        snap: int | None = None,
        cursor: str = "sb_h_double_arrow",
        on_move=None,
        on_press=None,
    ):
        self.canvas = canvas
        self.x = int(x)
        self.foreground = foreground
        self.background = background
        self.width_fg = width_fg
        self.width_bg = width_bg
        self.grab_px = grab_px
        self.bounds = bounds
        self.snap = snap
        self.cursor = cursor
        self.on_move = on_move
        self.on_press = on_press

        self._dragging = False
        self._cursor_set = False
        self._original_cursor = canvas.cget('cursor') or 'arrow'

        height = canvas.winfo_height() or int(canvas.cget("height") or 300)

        # 先畫背景線，再畫前景線（順序決定 Z-index）
        self.bg_line = canvas.create_line(self.x, 0, self.x, height,
                                          fill=self.background, width=self.width_bg)
        self.fg_line = canvas.create_line(self.x, 0, self.x, height,
                                          fill=self.foreground, width=self.width_fg)

        canvas.bind("<Button-1>", self._on_press, add="+")
        canvas.bind("<B1-Motion>", self._on_drag, add="+")
        canvas.bind("<ButtonRelease-1>", self._on_release, add="+")
        canvas.bind("<Motion>", self._on_motion, add="+")
        canvas.bind("<Configure>", self._on_resize, add="+")

    def _on_press(self, event):
        if self._near_line(event.x, event.y):
            if callable(self.on_press):
                self.on_press(self, event)
            self._dragging = True
            self.canvas.configure(cursor=self.cursor)

    def _on_drag(self, event):
        if not self._dragging:
            return
        new_x = event.x
        if self.bounds:
            new_x = max(self.bounds[0], min(self.bounds[1], new_x))
        if self.snap:
            new_x = round(new_x / self.snap) * self.snap
        if new_x != self.x:
            self.x = new_x
            self._redraw()
            if callable(self.on_move):
                self.on_move(self, self.x)

    def _on_release(self, _event):
        if self._dragging:
            self._dragging = False
            self._maybe_reset_cursor()

    def _on_motion(self, event):
        if not self._dragging and self._near_line(event.x, event.y):
            if not self._cursor_set:
                self._original_cursor = self.canvas.cget('cursor')
                self.canvas.configure(cursor=self.cursor)
                self._cursor_set = True
        else:
            self._maybe_reset_cursor()

    def _on_resize(self, _event):
        self._redraw()

    def _redraw(self):
        h = self.canvas.winfo_height()
        self.canvas.coords(self.bg_line, self.x, 0, self.x, h)
        self.canvas.coords(self.fg_line, self.x, 0, self.x, h)

    def _near_line(self, ex, ey):
        if ey < 0 or ey > self.canvas.winfo_height():
            return False
        return abs(ex - self.x) <= self.grab_px

    def _maybe_reset_cursor(self):
        if self._cursor_set and not self._dragging:
            self.canvas.configure(cursor=self._original_cursor)
            self._cursor_set = False

    def set_x(self, x: int):
        self.x = x
        self._redraw()
        if callable(self.on_move):
            self.on_move(self, self.x)

    def get_x(self) -> int:
        return self.x


# ----------------------
# Demo app
# ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Draggable Vertical Line Demo")

    # Top info bar
    info = tk.Label(
        root,
        text="Drag the lines left/right. They snap to 10 px and stay within the canvas.",
        anchor="w"
    )
    info.pack(fill="x", padx=10, pady=(10, 0))

    # Canvas
    canvas = tk.Canvas(root, width=800, height=400, bg="#f7f7f7", highlightthickness=0)
    canvas.pack(fill="both", expand=True, padx=10, pady=10)

    

    # Callback to update the status label
    def on_line_move(_line: DraggableVerticalLine, _x: int):
        print(f"Line moved to: {_x}")
        # status.set(f"L1: {line1.get_x()}, L2: {line2.get_x()}")

    # Create two draggable lines with different styles
    line = DraggableVerticalLine(
        canvas,
        x=300,
        foreground="#cccccc",# 淺線     
        background="#333333",# 深線     
        width_fg=2,
        width_bg=6,
        bounds=(50, 550),
        snap=10,
        on_move=on_line_move,
    )
  

    root.mainloop()
