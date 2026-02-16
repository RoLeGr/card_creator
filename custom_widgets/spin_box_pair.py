import tkinter as tk
from tkinter import ttk



class SpinBoxPair(ttk.Frame):
    def __init__(self, parent, value: tuple, padding: tuple, callback,
        label_spinbox_1=None,
        label_inter_spinbox=None,
        label_spinbox_2=None,
        spin_box_1_params=None,
        spin_box_2_params=None,
        *args,
        **frame_kwargs
    ):
        super().__init__(parent, *args, **frame_kwargs)

        spin_box_1_params = spin_box_1_params or {"from_": 0, "to": 10000, "width": 6}
        spin_box_2_params = spin_box_2_params or {"from_": 0, "to": 10000, "width": 6}

        # LABEL 1
        if label_spinbox_1:
            ttk.Label(self, text=label_spinbox_1).pack(side="left", padx=padding[0], pady=padding[1])

        # SPIN 1
        v1 = tk.IntVar(value=value[0])
        ttk.Spinbox(self, textvariable=v1, **spin_box_1_params).pack(
            side="left", padx=padding[0], pady=padding[1]
        )

        # Label between
        if label_inter_spinbox:
            ttk.Label(self, text=label_inter_spinbox).pack(
                side="left", padx=padding[0], pady=padding[1]
            )

        # LABEL 2
        if label_spinbox_2:
            ttk.Label(self, text=label_spinbox_2).pack(
                side="left", padx=padding[0], pady=padding[1]
            )

        # SPIN 2
        v2 = tk.IntVar(value=value[1])
        ttk.Spinbox(self, textvariable=v2, **spin_box_2_params).pack(
            side="left", padx=padding[0], pady=padding[1]
        )

        # Callback
        def update(*_):
            callback((v1.get(), v2.get()))

        v1.trace_add("write", update)
        v2.trace_add("write", update)
