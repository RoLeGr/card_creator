# Copyright (c) 2026 Le Gratiet Ronan
# Licensed under the MIT License.

import sys
from pathlib import Path
import pickle
import tkinter as tk
from tkinter import ttk, filedialog

from utils.printable_pdf_builder import PrintablePDFBuilder
from reportlab.lib.pagesizes import A4
from PIL import Image, ImageTk

from custom_widgets.CardPreview import CardPreview
from custom_widgets.spin_box_pair import SpinBoxPair
from custom_widgets.my_spin_box import MySpinBox
from custom_widgets.color_picker import ColorPicker
from custom_widgets.background_frame import BackgroundFrame
from custom_widgets.image_file_picker import ImageFilePicker



def get_exec_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    else:
        return Path(__file__).resolve().parent

def get_assets_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "assets"
    else:
        return Path(__file__).resolve().parent / "assets"

ROOT_DIR = get_exec_dir()
FONT_DIR = get_assets_dir()
BACKGROUND_DIR = FONT_DIR/"background_imgs"
GENERATE_DIR = ROOT_DIR / "generated"
CONFIG_DIR = ROOT_DIR / "config"   # dossier persistant utilisateur
ORIGIN_PIC_DIR = ROOT_DIR / "origin_pics"

for d in (CONFIG_DIR, GENERATE_DIR, ORIGIN_PIC_DIR):
    d.mkdir(exist_ok=True)
PARAMS_FILE = CONFIG_DIR / "params.pkl"

class IHM_Gen_cards(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.title('IHM création cartes à jouer')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f'{screen_width}x{screen_height}')

        self.style_definition()

        # IMG Loading
        image = Image.open(FONT_DIR/"directory.png")  # chemin de votre image
        image = image.resize((30, 30), Image.LANCZOS)
        photo_directory = ImageTk.PhotoImage(image)
        image = Image.open(FONT_DIR/"color_palette.png")  # chemin de votre image
        image = image.resize((30, 30), Image.LANCZOS)
        photo_color_palette = ImageTk.PhotoImage(image)
        image = Image.open(FONT_DIR / "save.png")  # chemin de votre image
        image = image.resize((60, 60), Image.LANCZOS)
        photo_save = ImageTk.PhotoImage(image)

        self.available_fonts = self.list_fonts()
        font_names = list(self.available_fonts.keys())

        # Main frames
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=0, minsize=450)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        frame_card_params = BackgroundFrame(main_frame, FONT_DIR/"image_back_card.png" , style="Params.TFrame")
        frame_card_params.grid(row=0, column=0, sticky="nsew")
        frame_right = ttk.Frame(main_frame, style="Main.TFrame")
        frame_right.grid(row=0, column=1, sticky="nsew")
        frame_right.grid_rowconfigure(0, weight=1)
        frame_right.grid_rowconfigure(1, weight=0)
        frame_right.grid_columnconfigure(0, weight=1)
        # grid pour frame_right
        frame_card_preview = ttk.Frame(frame_right, style="Card.TFrame")
        frame_card_preview.grid(row=0, column=0, sticky="nsew")
        frame_card_preview.grid_rowconfigure(0, weight=1)
        frame_card_preview.grid_columnconfigure(0, weight=1)
        frame_card_preview.grid_propagate(False)  # 🔒 indispensable

        frame_card_save = ttk.Frame(frame_right, style='Save.TFrame')
        frame_card_save.grid(row=1, column=0, sticky='ew')

        # configurer les poids
        frame_right.grid_rowconfigure(0, weight=1)  # preview prend tout l'espace vertical restant
        frame_right.grid_rowconfigure(1, weight=0)  # save bouton fixe
        frame_right.grid_columnconfigure(0, weight=1)  # toute la largeur
        frame_card_save.grid_columnconfigure(0, weight=1)
        frame_card_save.grid_columnconfigure(1, weight=1)
        frame_card_save.grid_columnconfigure(2, weight=1)
        button_save_config_default = ttk.Button(frame_card_save,
                                                text='Définir les paramètres actuel comme paramètres par défaut',
                                                style='Primary.TButton',
                                                command=self.save_params)
        button_save_config_default.grid(row=0, column=0, padx=10, pady=10)

        button_save_jpg = tk.Button(frame_card_save, image=photo_save, command=self.save_to_jpg)
        button_save_jpg.image = photo_save
        button_save_jpg.grid(row=0, column=1, padx=10, pady=10)

        # --- Canvas pour dégradé ---
        self.gradient_canvas = tk.Canvas(frame_card_preview, highlightthickness=0)
        self.gradient_canvas.grid(row=0, column=0, sticky="nsew")

        # Dessin du dégradé lors du redimensionnement
        self.gradient_canvas.bind("<Configure>", lambda e: self.draw_gradient())

        # --- CardPreview au-dessus du canvas ---
        self.card_preview = CardPreview(frame_card_preview)
        self.card_preview.grid(row=0, column=0, sticky='nsew')
        self.card_preview.tkraise()

        tabControl = ttk.Notebook(frame_card_params)
        frame_card_params.add_widget(tabControl)
        tab_carte = ttk.Frame(tabControl, style='notebook_label.TFrame')
        tab_background = ttk.Frame(tabControl, style='notebook_label.TFrame')
        tab_titre = ttk.Frame(tabControl, style='notebook_label.TFrame')
        tab_image = ttk.Frame(tabControl, style='notebook_label.TFrame')
        self.tab_text = ttk.Frame(tabControl, style='notebook_label.TFrame')
        tab_pdf = ttk.Frame(tabControl, style='notebook_label.TFrame')

        self.tab_text.grid_rowconfigure(0, weight=0)
        self.tab_text.grid_columnconfigure(0, weight=1)
        tabControl.add(tab_carte, text='Général')
        tabControl.add(tab_background, text='Arrière-plan')
        tabControl.add(tab_titre, text='Titre')
        tabControl.add(tab_image, text='Image')
        tabControl.add(self.tab_text, text='Texte')
        tabControl.add(tab_pdf, text='PDF')
        tabControl.bind("<<NotebookTabChanged>>", self.resize_notebook)

        # =========================
        # DEFAULT PARAMS
        # =========================
        self.params = {}
        load_ok = self.load_params()
        if not load_ok:
            self.params.setdefault("frame_dimensions", (1260, 1760))
            self.params.setdefault("card_bg_color", "green")
            self.params.setdefault("card_outline_color", "black")
            self.params.setdefault("card_outline_width", 10)

            self.params.setdefault("title", {
                "text": "",
                "font_size": 68,
                "color": "white",
                "title_position": (30, 10),
                "text_outline_color": "black"
            })

            self.params.setdefault("background", {
                "background_path": None,
                "display_background": False})
            self.params.setdefault("photo", {
                "frame_dimensions": (1200, 750),
                "frame_position": (30, 100),
                "frame_bg_color": "#EFD5B2",
                "background_opacity": 70,
                "frame_rounded_radius": 40,
                "frame_outline_color": "black",
                "frame_outline_width": 10,
                "photo_path": ""
            })

            self.params.setdefault("text", {
                "frame_dimensions": (1200, 850),
                "frame_position": (30, 870),
                "font_size_regular": 60,
                "font_size_bold": 60,
                "font_size_italic": 44,
                "text_color": "black",
                "frame_rounded_radius": 40,
                "padding": 60,
                "frame_outline_color": "black",
                "frame_outline_width": 10,
                "font_regular": "Lato-Regular.ttf",
                "font_bold": "Lato-Black.ttf",
                "font_italic": "Lato-Italic.ttf",
                "frame_bg_color": "#b4b4b4",
                "background_opacity": 70,
                "text_element": []
            })

        # =========================
        # PDF CREATION PARAMS
        # =========================
        self.pdf_conf = {
            "image_dir": str(GENERATE_DIR),
            "page_size": "A4",
            "printer_margin_mm": 10,
            "photo_width_mm": 63
        }

        # =========================
        # GENERAL tab
        # =========================
        row = 0

        ttk.Label(tab_carte, text="Dimensions de la carte (pixel) : ").grid(row=row, column=0, sticky="w",
                                                                         padx=(10, 5), pady=5)
        dim_card = SpinBoxPair(tab_carte,
                               self.params["frame_dimensions"],
                               (5, 5),
                               callback=lambda v: {self.params.update(frame_dimensions=v), self.refresh_preview()},
                               label_spinbox_1= "Largeur :",
                               label_spinbox_2="Hauteur :",
                               label_inter_spinbox= "x")
        dim_card.grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(tab_carte, text="Couleur de fond : ").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        ColorPicker(tab_carte, callback=lambda v: {self.params.update(card_bg_color=v), self.refresh_preview()},
                    init_value=self.params["card_bg_color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(tab_carte, text="Couleur contour : ").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        ColorPicker(tab_carte, callback=lambda v: {self.params.update(card_outline_color=v), self.refresh_preview()},
                    init_value=self.params["card_outline_color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        # Rayon coins
        ttk.Label(tab_carte, text="Largeur de la bordure (pixels) : ").grid(row=row, column=0, sticky="w",
                                                                         padx=(10, 5), pady=5)
        MySpinBox(tab_carte, callback=lambda v: {self.params.update(card_outline_width=v), self.refresh_preview()},
                  init_value=self.params["card_outline_width"],
                  from_=0, to=300, width=6).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1

        # =========================
        # BACKGROUND tab
        # =========================
        def background_changed(new_config):
            print("Background mis à jour :", new_config)
        ImageFilePicker(tab_background, self._get_list_predifined_background(), self.params["background"],
                        on_change_callback=lambda v: {self.params["background"].update(frame_dimensions=v),
                                                      self.refresh_preview()}).grid(row=0, column=0, sticky="w",
                                                                                    padx=(10, 5), pady=5)

        # =========================
        # TITLE tab
        # =========================
        row = 0
        title = self.params["title"]

        ttk.Label(tab_titre, text="Titre de la carte :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        t_var = tk.StringVar(value=title["text"])
        ttk.Entry(tab_titre, textvariable=t_var).grid(row=row, column=1, columnspan=2, sticky="ew",
                                                      padx=(15, 10), pady=10)

        t_var.trace_add("write", lambda *_: (
            title.update(text=t_var.get()),
            self.refresh_preview()
        ))
        row += 1

        ttk.Label(tab_titre, text="Taille police :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(tab_titre, callback=lambda v: {title.update(font_size=v), self.refresh_preview()},
                  init_value=title["font_size"],
                  from_=4, to=300, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)

        row += 1

        ttk.Label(tab_titre, text="Couleur texte :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        ColorPicker(tab_titre, callback=lambda v: {title.update(color=v), self.refresh_preview()},
                    init_value=title["color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(tab_titre, text="Position :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        SpinBoxPair(tab_titre,
                    title["title_position"],
                    (5, 5),
                    callback=lambda v: {title.update(title_position=v), self.refresh_preview()},
                    label_spinbox_1="X :",
                    label_spinbox_2="Y :",
                    label_inter_spinbox=" - ").grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)

        # =========================
        # PICTURE tab
        # =========================
        photo = self.params["photo"]
        row = 0

        ttk.Label(tab_image, text="Dimensions cadre :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        SpinBoxPair(tab_image,
                    photo["frame_dimensions"],
                    (5, 5),
                    callback=lambda v: {photo.update(frame_dimensions=v), self.refresh_preview()},
                    label_spinbox_1="Largeur :",
                    label_spinbox_2="Hauteur :",
                    label_inter_spinbox="*").grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(tab_image, text="Position :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        SpinBoxPair(tab_image,
                    photo["frame_position"],
                    (5, 5),
                    callback=lambda v: {photo.update(frame_position=v), self.refresh_preview()},
                    label_spinbox_1="X :",
                    label_spinbox_2="Y :",
                    label_inter_spinbox=" - ").grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)

        row += 1

        ttk.Label(tab_image, text="Rayon coins :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(tab_image, callback=lambda v: {photo.update(frame_rounded_radius=v), self.refresh_preview()},
                  init_value=photo["frame_rounded_radius"],
                  from_=4, to=300, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1

        ttk.Label(tab_image, text="Largeur contour :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(tab_image, callback=lambda v: {photo.update(frame_outline_width=v), self.refresh_preview()},
                  init_value=photo["frame_outline_width"],
                  from_=4, to=300, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)

        row += 1

        ttk.Label(tab_image, text="Couleur contour :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        ColorPicker(tab_image, callback=lambda v: {photo.update(frame_outline_color=v), self.refresh_preview()},
                    init_value=photo["frame_outline_color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)

        row += 1


        ttk.Label(tab_image, text="Couleur fond :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        ColorPicker(tab_image, callback=lambda v: {photo.update(frame_bg_color=v), self.refresh_preview()},
                    init_value=photo["frame_bg_color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)

        row += 1

        ttk.Label(tab_image, text="Opacité fond :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(tab_image, callback=lambda v: {photo.update(background_opacity=v), self.refresh_preview()},
                  init_value=photo["background_opacity"],
                  from_=0, to=100, width=4).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1

        ttk.Label(tab_image, text="Image :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        frame_path_image = ttk.Frame(tab_image)
        img_var = tk.StringVar(value=photo["photo_path"])
        ttk.Entry(frame_path_image, textvariable=img_var, width=35).grid(row=0, column=0)
        def browse():
            path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.jpg *.jpeg")],
                initialdir=ORIGIN_PIC_DIR
            )
            if path:
                img_var.set(path)
        btn = tk.Button(frame_path_image, image=photo_directory, command=browse)
        btn.image = photo_directory
        btn.grid(row=0, column=1)
        img_var.trace_add("write", lambda *_: (
            photo.update(photo_path=img_var.get()),
            self.refresh_preview()
        ))
        frame_path_image.grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)


        # =========================
        # TEXT tab
        # =========================
        text_conf = self.params["text"]

        text_options_frame = ttk.Frame(self.tab_text)
        text_options_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        text_options_frame.grid_columnconfigure(1, weight=1)

        row = 0

        ttk.Label(text_options_frame, text="Dimensions cadre texte :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        SpinBoxPair(text_options_frame,
                    text_conf["frame_dimensions"],
                    (5, 5),
                    callback=lambda v: {text_conf.update(frame_dimensions=v), self.refresh_preview()},
                    label_spinbox_1="Largeur :",
                    label_spinbox_2="Hauteur :",
                    label_inter_spinbox="*").grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(text_options_frame, text="Position cadre texte :").grid(row=row, column=0, sticky="w", padx=(10, 5),
                                                                            pady=5)
        SpinBoxPair(text_options_frame,
                    text_conf["frame_position"],
                    (5, 5),
                    callback=lambda v: {text_conf.update(frame_position=v), self.refresh_preview()},
                    label_spinbox_1="X :",
                    label_spinbox_2="Y :",
                    label_inter_spinbox=" - ").grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)

        row += 1

        ttk.Label(text_options_frame, text="Rayon coins :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(text_options_frame, callback=lambda v: {text_conf.update(frame_rounded_radius=v), self.refresh_preview()},
                  init_value=text_conf["frame_rounded_radius"],
                  from_=4, to=300, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1

        ttk.Label(text_options_frame, text="Largeur contour :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(text_options_frame,
                  callback=lambda v: {text_conf.update(frame_outline_width=v), self.refresh_preview()},
                  init_value=text_conf["frame_outline_width"],
                  from_=0, to=300, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1

        ttk.Label(text_options_frame, text="Padding texte :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(text_options_frame,
                  callback=lambda v: {text_conf.update(padding=v), self.refresh_preview()},
                  init_value=text_conf["padding"],
                  from_=0, to=1000, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1

        ttk.Label(text_options_frame, text="Couleur du texte :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        ColorPicker(text_options_frame, callback=lambda v: {text_conf.update(text_color=v), self.refresh_preview()},
                    init_value=text_conf["text_color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(text_options_frame, text="Fond du cadre texte :").grid(row=row, column=0, sticky="w", padx=(10, 5),
                                                                      pady=5)
        ColorPicker(text_options_frame, callback=lambda v: {text_conf.update(frame_bg_color=v), self.refresh_preview()},
                    init_value=text_conf["frame_bg_color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(text_options_frame, text="Opacité fond :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(text_options_frame, callback=lambda v: {text_conf.update(background_opacity=v), self.refresh_preview()},
                  init_value=text_conf["background_opacity"],
                  from_=0, to=100, width=4).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1

        ttk.Label(text_options_frame, text="Contour du cadre texte :").grid(row=row, column=0, sticky="w", padx=(10, 5),
                                                                         pady=5)
        ColorPicker(text_options_frame, callback=lambda v: {text_conf.update(frame_outline_color=v),
                                                            self.refresh_preview()},
                    init_value=text_conf["frame_outline_color"], image_button=photo_color_palette,
                    padding=(5, 5)).grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(text_options_frame, text="Police texte :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        font_reg_frame = ttk.Frame(text_options_frame)
        self.font_regular_var = tk.StringVar(value=text_conf.get("font_regular"))
        font_combo = ttk.Combobox(
            font_reg_frame,
            values=font_names,
            textvariable=self.font_regular_var,
            state="readonly",
            width=25
        )
        font_combo.grid(row=row, column=1, sticky="w", padx=5)

        ttk.Label(font_reg_frame, text="Taille").grid(row=row, column=2, sticky="e")

        fs_reg = tk.IntVar(value=text_conf["font_size_regular"])
        ttk.Spinbox(font_reg_frame, from_=5, to=200, textvariable=fs_reg, width=5) \
            .grid(row=row, column=3, sticky="w", padx=5)

        self.font_regular_var.trace_add("write",
                                        lambda *_: (
                                            text_conf.update(
                                                font_regular=self.available_fonts[self.font_regular_var.get()]
                                            ),
                                            self.refresh_preview()
                                        )
                                        )

        fs_reg.trace_add("write",
                         lambda *_: (
                             text_conf.update(font_size_regular=fs_reg.get()),
                             self.refresh_preview()
                         )
                         )
        font_reg_frame.grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(text_options_frame, text="Police titre :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        font_bold_frame = ttk.Frame(text_options_frame)
        self.font_bold_var = tk.StringVar(value=text_conf.get("font_bold"))
        font_combo = ttk.Combobox(
            font_bold_frame,
            values=font_names,
            textvariable=self.font_bold_var,
            state="readonly",
            width=25
        )
        font_combo.grid(row=0, column=0, sticky="w", padx=5)

        ttk.Label(font_bold_frame, text="Taille").grid(row=0, column=1, sticky="e")

        fs_bold = tk.IntVar(value=text_conf["font_size_bold"])
        ttk.Spinbox(font_bold_frame, from_=5, to=200, textvariable=fs_bold, width=5) \
            .grid(row=0, column=2, sticky="w", padx=5)

        self.font_bold_var.trace_add("write",
                                        lambda *_: (
                                            text_conf.update(
                                                font_bold=self.available_fonts[self.font_bold_var.get()]
                                            ),
                                            self.refresh_preview()
                                        )
                                        )

        fs_bold.trace_add("write",
                          lambda *_: (
                              text_conf.update(font_size_bold=fs_bold.get()),  # CORRECT
                              self.refresh_preview()
                          )
                          )
        font_bold_frame.grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        ttk.Label(text_options_frame, text="Police commentaire :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        font_italic_frame = ttk.Frame(text_options_frame)
        self.font_italic_var = tk.StringVar(value=text_conf.get("font_italic"))
        font_combo = ttk.Combobox(
            font_italic_frame,
            values=font_names,
            textvariable=self.font_italic_var,
            state="readonly",
            width=25
        )
        font_combo.grid(row=row, column=1, sticky="w", padx=5)

        ttk.Label(font_italic_frame, text="Taille").grid(row=row, column=2, sticky="e")

        fs_italic = tk.IntVar(value=text_conf["font_size_italic"])
        ttk.Spinbox(font_italic_frame, from_=5, to=200, textvariable=fs_italic, width=5) \
            .grid(row=row, column=3, sticky="w", padx=5)

        self.font_italic_var.trace_add("write",
                                        lambda *_: (
                                            text_conf.update(
                                                font_italic=self.available_fonts[self.font_italic_var.get()]
                                            ),
                                            self.refresh_preview()
                                        )
                                        )

        fs_italic.trace_add("write",
                         lambda *_: (
                             text_conf.update(font_size_italic=fs_italic.get()),
                             self.refresh_preview()
                         )
                         )
        font_italic_frame.grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        row += 1

        blocks_frame = ttk.Frame(self.tab_text)
        blocks_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        blocks_frame.grid_rowconfigure(0, weight=0)  # bouton
        blocks_frame.grid_rowconfigure(1, weight=1)  # zone scrollable

        blocks_frame.grid_columnconfigure(0, weight=1)  # canvas prend tout
        blocks_frame.grid_columnconfigure(1, weight=0)  # scrollbar fixe
        self.tab_text.grid_rowconfigure(1, weight=1)

        canvas = tk.Canvas(blocks_frame, highlightthickness=0)
        canvas.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(blocks_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")

        canvas.configure(yscrollcommand=scrollbar.set)

        elements_frame = ttk.Frame(canvas)
        elements_frame.grid_columnconfigure(0, weight=1)

        canvas_window = canvas.create_window((0, 0), window=elements_frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        elements_frame.bind("<Configure>", on_configure)

        def resize_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_frame)

        add_btn = ttk.Button(
            blocks_frame,
            text="+ Ajouter un bloc",
            command=lambda: (
                text_conf["text_element"].append({"title": "", "texte": "", "comment": ""}),
                redraw_elements(),
                self.refresh_preview()
            )
        )
        add_btn.grid(row=0, column=0, pady=(0, 10), sticky="w")


        def redraw_elements():
            for w in elements_frame.winfo_children():
                w.destroy()

            for el in text_conf["text_element"]:
                frame = ttk.LabelFrame(elements_frame, text="Bloc de texte")
                frame.grid(sticky="ew", pady=5)
                frame.grid_columnconfigure(1, weight=1)

                for i, key in enumerate(("title", "texte", "comment")):
                    ttk.Label(frame, text=key.capitalize()).grid(row=i, column=0, sticky="w", padx=5, pady=2)
                    var = tk.StringVar(value=el.get(key, ""))
                    ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="ew", padx=5, pady=2)

                    var.trace_add(
                        "write",
                        lambda *_,
                               e=el, k=key, v=var: (
                            e.update({k: v.get()}),
                            self.refresh_preview()
                        )
                    )

                ttk.Button(
                    frame,
                    text="Supprimer",
                    command=lambda e=el: (
                        text_conf["text_element"].remove(e),
                        redraw_elements(),
                        self.refresh_preview()
                    )
                ).grid(row=3, column=1, sticky="e", padx=5, pady=5)

        redraw_elements()

        ttk.Label(tab_pdf, text="Dossier images :").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        img_dir_var = tk.StringVar(value=self.pdf_conf["image_dir"])
        frame_select = ttk.Frame(tab_pdf)
        frame_select.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_select, textvariable=img_dir_var, width=35).grid(row=row, column=1, sticky="w", padx=(5, 0))

        def browse_img_dir():
            path = filedialog.askdirectory(initialdir=GENERATE_DIR)
            if path:
                img_dir_var.set(path)

        btn = tk.Button(frame_select, image=photo_directory, command=browse_img_dir)
        btn.image = photo_directory
        btn.grid(row=row, column=2)
        img_dir_var.trace_add("write", lambda *_: self.pdf_conf.update(image_dir=img_dir_var.get()))

        row += 1

        ttk.Label(tab_pdf, text="Marge imprimante (mm) :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(tab_pdf,
                  callback=lambda v: {self.pdf_conf.update(printer_margin_mm=v), self.refresh_preview()},
                  init_value=self.pdf_conf["printer_margin_mm"],
                  from_=0, to=150, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)
        row += 1
        ttk.Label(tab_pdf, text="Largeur carte (mm) :").grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)
        MySpinBox(tab_pdf,
                  callback=lambda v: {self.pdf_conf.update(photo_width_mm=v), self.refresh_preview()},
                  init_value=self.pdf_conf["photo_width_mm"],
                  from_=1, to=300, width=5).grid(row=row, column=1, sticky="w", padx=(15, 10), pady=10)

        row += 1

        ttk.Label(tab_pdf, text="La hauteur de la photo est calculée pour conserver le bon ratio "
                                "w*h.").grid(row=row, column=0, sticky="w", padx=5, pady=5, columnspan=2)
        row += 1

        ttk.Label(tab_pdf, text="Attention: Toutes les cartes du dossier doivent avoir la même dimension en "
                                "pixel").grid(row=row, column=0, sticky="w", padx=5, pady=5, columnspan=2)
        row += 1

        button_save_jpg = ttk.Button(tab_pdf, text='Créer un pdf contenant plusieurs cartes',
                                     style='Primary.TButton',
                                     command=self.create_pdf)
        button_save_jpg.grid(row=row, column=0, columnspan=3, padx=10, pady=10)
        button_save_jpg.grid_configure(sticky="")  # ou sticky="n" pour juste vertical

        self.refresh_preview()


    def style_definition(self):
        style = ttk.Style()
        style.theme_use('default')  # or 'clam', 'alt', 'vista' (Windows)

        style.configure(
            "TButton",
            background="#FDFD96",
            foreground="black",
            padding=4,
            relief="raise"
        )
        style.map(
            "TButton",
            background=[
                ("active", "#FDFD20"),
                ("pressed", "#FDFD00")
            ],
            foreground=[
                ("active", "black"),
                ("pressed", "black")
            ]
        )

        style.configure('Params.TFrame', background='white')
        style.configure('Card.TFrame', background='white')
        style.configure('Main.TFrame', background='white')
        style.configure('Save.TFrame', background='#F0F0F0')
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10))

    def save_to_jpg(self):
        img = self.card_preview.create_card_image(self.params)
        path = filedialog.asksaveasfilename(
            title="Sauvegarder la carte sous...",
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg")],
            initialdir=GENERATE_DIR,
            initialfile=f"Carte {self.params["title"]["text"]}.jpg"
        )
        if path:
            img.convert("RGB").save(path, "JPEG", quality=95)

    def refresh_preview(self):
        self.card_preview.update_params(self.params, refresh_preview=True)


    def save_params(self):
        with open(PARAMS_FILE, "wb") as f:
            pickle.dump(self.params, f)

    def load_params(self):
        if PARAMS_FILE.exists():
            with open(PARAMS_FILE, "rb") as f:
                self.params = pickle.load(f)
            return True
        return False

    def list_fonts(self) -> dict:
        """
        Retourne un dictionnaire {nom_police: chemin} pour tous les .ttf et .otf dans FONT_DIR
        """
        font_files = list(FONT_DIR.glob("*.ttf")) + list(FONT_DIR.glob("*.otf"))
        return {f.stem: f for f in font_files}

    def create_pdf(self):
        page_size = A4 if self.pdf_conf["page_size"] == "A4" else None

        builder = PrintablePDFBuilder(
            image_dir=self.pdf_conf["image_dir"],
            page_size=page_size,
            printer_margin_mm=self.pdf_conf["printer_margin_mm"],
            photo_width_mm=self.pdf_conf["photo_width_mm"]
        )
        builder.generate_pdf()

    def resize_notebook(self, event):
        notebook = event.widget
        selected_tab = notebook.nametowidget(notebook.select())

        self.update_idletasks()

        parent = notebook.master
        parent_height = parent.winfo_height()

        bottom_margin = 40

        if selected_tab == self.tab_text:
            max_height = parent_height - bottom_margin
            notebook.config(height=max_height)

            self.tab_text.grid_rowconfigure(1, weight=1)

        else:
            req_height = selected_tab.winfo_reqheight()
            final_height = min(req_height, parent_height - bottom_margin)
            notebook.config(height=final_height)
            self.tab_text.grid_rowconfigure(1, weight=0)

    def draw_gradient(self):
        canvas = self.gradient_canvas
        canvas.delete("gradient")

        height = canvas.winfo_height()
        width = canvas.winfo_width()
        if height < 2 or width < 2:
            return

        color1 = "#ffffff"
        color2 = "#000000"

        r1, g1, b1 = canvas.winfo_rgb(color1)
        r2, g2, b2 = canvas.winfo_rgb(color2)

        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height

        for i in range(height):
            nr = int(r1 + r_ratio * i) // 256
            ng = int(g1 + g_ratio * i) // 256
            nb = int(b1 + b_ratio * i) // 256
            canvas.create_line(0, i, width, i, fill=f"#{nr:02x}{ng:02x}{nb:02x}", tags="gradient")

    def _get_list_predifined_background(self):
        image_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        image_files = [f.resolve() for f in BACKGROUND_DIR.iterdir() if f.suffix.lower() in image_exts]
        return image_files

if __name__ == '__main__':
    ihm = IHM_Gen_cards()
    ihm.mainloop()
