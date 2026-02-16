import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path


class ImageFilePicker(ttk.Frame):
    def __init__(
        self,
        parent,
        predefined_paths: list[Path],
        config_dict: dict,
        on_change_callback=None,
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        self.config_dict = config_dict
        self.on_change_callback = on_change_callback

        # Nettoyage + validation des paths
        self.predefined_paths = [Path(p).resolve() for p in predefined_paths]

        # Mapping nom affiché -> Path absolu
        self.name_to_path = {
            p.name: p for p in self.predefined_paths
        }

        self.mode = tk.StringVar()
        self.selected_file_path = tk.StringVar()

        # ======================
        # RADIO BUTTONS
        # ======================
        radio_frame = ttk.Frame(self)
        radio_frame.grid(row=0, column=0, sticky="ns", padx=(0, 15))

        ttk.Radiobutton(
            radio_frame,
            text="Aucun fond",
            variable=self.mode,
            value="none",
            command=self._state_changed
        ).pack(anchor="w", pady=2)

        ttk.Radiobutton(
            radio_frame,
            text="Image prédéfinie",
            variable=self.mode,
            value="list",
            command=self._state_changed
        ).pack(anchor="w", pady=2)

        ttk.Radiobutton(
            radio_frame,
            text="Fichier local",
            variable=self.mode,
            value="file",
            command=self._state_changed
        ).pack(anchor="w", pady=2)

        # ======================
        # ZONE CONTENU
        # ======================
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky="ew")
        self.columnconfigure(1, weight=1)

        # Bloc liste
        self.list_frame = ttk.Frame(self.content_frame)
        ttk.Label(self.list_frame, text="Choisir une image :").pack(anchor="w")

        self.combo = ttk.Combobox(
            self.list_frame,
            state="readonly",
            values=list(self.name_to_path.keys())
        )
        self.combo.pack(fill="x", pady=5)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self._state_changed())

        # Bloc fichier
        self.file_frame = ttk.Frame(self.content_frame)
        ttk.Label(self.file_frame, text="Sélectionner un fichier :").pack(anchor="w")

        file_row = ttk.Frame(self.file_frame)
        file_row.pack(fill="x", pady=5)

        self.file_entry = ttk.Entry(
            file_row,
            textvariable=self.selected_file_path
        )
        self.file_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(
            file_row,
            text="Parcourir",
            command=self._browse_file
        ).pack(side="right")

        self._initialize_from_config()
        self._update_view()



    def _initialize_from_config(self):
        display = self.config_dict.get("display_background", False)
        background_path = self.config_dict.get("background_path")

        if not display:
            self.mode.set("none")
            return

        if background_path:
            background_path = Path(background_path).resolve()

            if background_path in self.predefined_paths:
                self.mode.set("list")
                self.combo.set(background_path.name)
            else:
                self.mode.set("file")
                self.selected_file_path.set(str(background_path))
        else:
            self.mode.set("none")

    # ==========================================
    # LOGIQUE INTERNE
    # ==========================================

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if file_path:
            self.selected_file_path.set(file_path)
            self._state_changed()

    def _state_changed(self):
        self._update_view()
        self._update_config()

        if self.on_change_callback:
            self.on_change_callback(self.config_dict)

    def _update_view(self):
        self.list_frame.grid_remove()
        self.file_frame.grid_remove()

        if self.mode.get() == "list":
            self.list_frame.grid(row=0, column=0, sticky="ew")

        elif self.mode.get() == "file":
            self.file_frame.grid(row=0, column=0, sticky="ew")

    def _update_config(self):
        mode = self.mode.get()

        if mode == "none":
            self.config_dict["display_background"] = False
            self.config_dict["background_path"] = None
            return

        self.config_dict["display_background"] = True

        if mode == "list":
            selected_name = self.combo.get()
            self.config_dict["background_path"] = (
                self.name_to_path.get(selected_name)
            )

        elif mode == "file":
            path_str = self.selected_file_path.get()
            self.config_dict["background_path"] = (
                Path(path_str).resolve() if path_str else None
            )