import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class BackgroundFrame(ttk.Frame):
    def __init__(self, parent, image_path, **kwargs):
        super().__init__(parent, **kwargs)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.original_image = Image.open(image_path)
        self.tk_image = None
        self.image_id = None
        self.window_id = None

        self.canvas.bind("<Configure>", self._resize)

    def _update_canvas_size(self, event):
        req_w = event.width
        req_h = event.height

        # Adapter la taille du canvas au notebook
        self.canvas.config(width=req_w, height=req_h)

    def add_widget(self, widget):
        self.window_id = self.canvas.create_window(
            0, 0, anchor="nw", window=widget
        )

        widget.bind("<Configure>", self._update_canvas_size)

    def _resize(self, event):
        w, h = event.width, event.height
        img_w, img_h = self.original_image.size

        left = max((img_w - w) // 2, 0)
        top = max((img_h - h) // 2, 0)
        right = min(left + w, img_w)
        bottom = min(top + h, img_h)

        cropped = self.original_image.crop((left, top, right, bottom))
        self.tk_image = ImageTk.PhotoImage(cropped)

        if self.image_id is None:
            self.image_id = self.canvas.create_image(
                0, 0, anchor="nw", image=self.tk_image
            )
        else:
            self.canvas.itemconfig(self.image_id, image=self.tk_image)

        # ⚠️ NE PAS forcer width/height du window
        if self.window_id:
            self.canvas.coords(self.window_id, 0, 0)