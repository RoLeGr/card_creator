import tkinter as tk
from tkinter import ttk



class MySpinBox(ttk.Spinbox):
    def __init__(self, parent, callback, init_value=0,
        *args,
        **kwargs
    ):
        v1 = tk.IntVar(value=init_value)
        kwargs["textvariable"] = v1
        super().__init__(parent, *args, **kwargs)

        # Callback
        def update(*_):
            callback(v1.get())
        v1.trace_add("write", update)
