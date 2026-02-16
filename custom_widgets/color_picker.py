import tkinter as tk
from tkinter import ttk, colorchooser



class ColorPicker(ttk.Frame):
    def __init__(self, parent, callback, padding: tuple, init_value="black", label_picker=None, image_button=None, entry_params=None, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)

        # LABEL
        if label_picker:
            ttk.Label(self, text=label_picker).pack(side="left", padx=padding[0], pady=padding[1])

        # ENTRY
        var = tk.StringVar(value=init_value)
        entry_params = entry_params or {"width": 12}
        entry_params["textvariable"] = var
        entry = ttk.Entry(self, **entry_params)
        entry.pack(side="left", padx=padding[0], pady=padding[1])


        def choose():
            color = colorchooser.askcolor(color=var.get())[1]
            if color:
                var.set(color)
        if image_button:
            btn = tk.Button(self, image=image_button, command=choose)
            btn.image = image_button  # ← garder la référence
            btn.pack(side="left")
        else:
            ttk.Button(self, text="Choisir couleur", width=20, command=choose).pack(side="left")

        # Callback
        def update(*_):
            callback(var.get())

        var.trace_add("write", update)
