# Copyright (c) 2026 Le Gratiet Ronan
# Licensed under the MIT License.

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageColor

class CardPreview(tk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.params = {}
        self.padx = 0
        self.pady = 0

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=self.padx, pady=self.pady)

        self.img_hd = None
        self.tk_image = None

        self.canvas.bind("<Configure>", lambda e: self.refresh_preview())

    def update_params(self, new_params: dict, refresh_preview=True):
        self.params.update(new_params)
        if refresh_preview:
            self.refresh_preview()

    def refresh_preview(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 2 or height < 2:
            return

        gradient_img = Image.new("RGB", (width, height), color=0)
        r1, g1, b1 = (255, 255, 255)  # haut
        r2, g2, b2 = (160, 196, 255)  # bas
        for y in range(height):
            nr = int(r1 + (r2 - r1) * y / height)
            ng = int(g1 + (g2 - g1) * y / height)
            nb = int(b1 + (b2 - b1) * y / height)
            gradient_img.paste((nr, ng, nb), [0, y, width, y + 1])

        if self.params:
            card_img = self.create_card_image(self.params)
            scale = min(width / card_img.width, height / card_img.height)
            new_size = (max(1, int(card_img.width * scale)), max(1, int(card_img.height * scale)))
            card_img = card_img.resize(new_size, Image.LANCZOS)
            x = (width - new_size[0]) // 2
            y = (height - new_size[1]) // 2
            gradient_img.paste(card_img, (x, y))

        self.tk_image = ImageTk.PhotoImage(gradient_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def _draw_rectangle(
            self,
            img,
            position: tuple,
            dimensions: tuple,
            color,
            round_radius=0,
            outline_color="black",
            outline_width=0,
            opacity=100
    ):
        """
        Parameters
        ----------
        img
        position
        dimensions
        color
        round_radius
        outline_color
        outline_width
        opacity: int
            0 - 100 (0 = transparent)
        Returns
        -------

        """
        x0, y0 = position
        w, h = dimensions
        opacity = int((opacity)*255/100)

        if img.mode != "RGBA":
            img = img.convert("RGBA")

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        if color is None:
            fill_color = None
        elif isinstance(color, str):
            r, g, b = ImageColor.getrgb(color)
            fill_color = (r, g, b, opacity)
        elif isinstance(color, tuple):
            if len(color) == 4:
                r, g, b, _ = color
            else:
                r, g, b = color
            fill_color = (r, g, b, opacity)
        else:
            raise ValueError("Format de couleur non supporté")


        if not outline_width:
            draw.rounded_rectangle(
                [x0, y0, x0 + w, y0 + h],
                round_radius,
                fill=fill_color
            )
        else:
            draw.rounded_rectangle(
                [x0, y0, x0 + w, y0 + h],
                round_radius,
                fill=fill_color,
                outline=outline_color,
                width=outline_width
            )

        img.alpha_composite(overlay)

        return img

    def _add_photo(self, img_card, params_photo: dict):
        frame_w, frame_h = params_photo["frame_dimensions"][0], params_photo["frame_dimensions"][1]
        frame_w -= params_photo["frame_outline_width"] * 2
        frame_h -= params_photo["frame_outline_width"] * 2
        frame_x, frame_y = params_photo["frame_position"]
        frame_x += params_photo["frame_outline_width"]
        frame_y += params_photo["frame_outline_width"]
        if not params_photo["photo_path"]:
            return
        img_photo = Image.open(params_photo["photo_path"])

        scale = min(frame_w / img_photo.width, frame_h / img_photo.height)
        new_w, new_h = int(img_photo.width*scale), int(img_photo.height*scale)
        img_photo = img_photo.resize((new_w, new_h), Image.LANCZOS)

        paste_x = frame_x + (frame_w - new_w)//2
        paste_y = frame_y + (frame_h - new_h)//2

        if img_photo.mode == "RGBA":
            img_card.paste(img_photo, (paste_x, paste_y), img_photo)
        else:
            img_card.paste(img_photo, (paste_x, paste_y))

    def _add_card_text(self, img_card, text_params):
        try:
            font_regular = ImageFont.truetype(text_params["font_regular"], text_params["font_size_regular"])
            font_bold = ImageFont.truetype(text_params["font_bold"], text_params["font_size_bold"])
            font_italic = ImageFont.truetype(text_params["font_italic"], text_params["font_size_italic"])
        except:
            font_regular = font_bold = font_italic = ImageFont.load_default()

        frame_x, frame_y = text_params["frame_position"]
        frame_x += text_params["padding"]
        frame_y += text_params["padding"]
        frame_w, frame_h = text_params["frame_dimensions"]
        frame_w -= text_params["padding"] * 2
        frame_h -= text_params["padding"] * 2
        draw = ImageDraw.Draw(img_card)

        x_start = frame_x + 5
        y = frame_y + 5
        line_spacing = 4

        line_height = max(
            font_regular.getbbox("Hg")[3] - font_regular.getbbox("Hg")[1],
            font_bold.getbbox("Hg")[3] - font_bold.getbbox("Hg")[1],
            font_italic.getbbox("Hg")[3] - font_italic.getbbox("Hg")[1]
        ) + line_spacing

        section_spacing = int(line_height * 1.5)

        def draw_wrapped_text(text, font, x, y, max_width, fill="black"):
            words = text.split()
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
                if line_width <= max_width:
                    current_line = test_line
                else:
                    draw.text((x, y), current_line, font=font, fill=fill)
                    y += line_height
                    current_line = word
            if current_line:
                draw.text((x, y), current_line, font=font, fill=fill)
                y += line_height
            return y

        for section in text_params["text_element"]:
            title = section.get("title", "")
            texte = section.get("texte", "")
            comment = section.get("comment", "")

            max_width = frame_w - 10

            # --- Dessiner le titre + première ligne de texte ---
            if title:
                bbox_title = draw.textbbox((0, 0), title, font=font_bold)
                title_width = bbox_title[2] - bbox_title[0]

                x_text = x_start + title_width  # texte après titre
                words = texte.split() if texte else []
                line = ""
                y_line = y

                # Première ligne : titre + texte jusqu'à largeur max
                for i, word in enumerate(words):
                    test_line = line + (" " if line else "") + word
                    bbox = draw.textbbox((0, 0), test_line, font=font_regular)
                    if bbox[2] - bbox[0] + title_width <= max_width:
                        line = test_line
                    else:
                        break  # dépassement de largeur

                # Dessiner titre
                draw.text((x_start, y_line), title, font=font_bold, fill="black")
                # Dessiner première partie du texte sur la même ligne
                if line:
                    draw.text((x_text, y_line), line, font=font_regular, fill="black")

                # Mettre à jour y et supprimer les mots déjà dessinés
                y += line_height
                words = words[len(line.split()):]

                # Dessiner les lignes suivantes du texte
                if words:
                    y = draw_wrapped_text(" ".join(words), font_regular, x_start, y, max_width)

            else:
                # Pas de titre, texte normal
                if texte:
                    y = draw_wrapped_text(texte, font_regular, x_start, y, max_width)

            # Dessiner commentaire
            if comment:
                y = draw_wrapped_text(comment, font_italic, x_start, y, max_width, fill="black")

            y += section_spacing - line_height

    def _add_background_image(self, img_card: Image, params: dict):
        background_path = params.get("background_path")
        if not background_path:
            return img_card

        opacity = params.get("opacity", 255)
        keep_ratio = params.get("keep_ratio", False)

        if img_card.mode != "RGBA":
            img_card = img_card.convert("RGBA")

        width, height = img_card.size

        bg = Image.open(background_path).convert("RGBA")

        if keep_ratio:
            bg.thumbnail((width, height), Image.LANCZOS)

            background_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            x = (width - bg.width) // 2
            y = (height - bg.height) // 2
            background_layer.paste(bg, (x, y))
            bg = background_layer
        else:
            bg = bg.resize((width, height), Image.LANCZOS)

        if opacity < 255:
            alpha = bg.split()[3]
            alpha = alpha.point(lambda p: p * (opacity / 255))
            bg.putalpha(alpha)

        # --- Fusion ---
        img_card.alpha_composite(bg)

        return img_card

    def create_card_image(self, params: dict) -> Image.Image:
        card_w, card_h = params["frame_dimensions"]
        img_card = Image.new("RGB", (card_w, card_h), params["card_bg_color"])

        if params["background"]["display_background"]:
            img_card = self._add_background_image(img_card, {"background_path": params["background"]["background_path"]})
            img_card = self._draw_rectangle(img_card, (0, 0), (card_w, card_h),
                                            None,
                                            outline_color=params["card_outline_color"],
                                            outline_width=params["card_outline_width"],
                                            opacity=0)
        else:
            img_card = self._draw_rectangle(img_card, (0, 0), (card_w, card_h),
                                            None,
                                            outline_color=params["card_outline_color"],
                                            outline_width=params["card_outline_width"])

        # Cadre photo
        params_photo = params.get("photo", {})
        img_card = self._draw_rectangle(img_card, params_photo["frame_position"], params_photo["frame_dimensions"],
                                        params_photo["frame_bg_color"], params_photo["frame_rounded_radius"],
                                        outline_color=params_photo["frame_outline_color"],
                                        outline_width=params_photo["frame_outline_width"],
                                        opacity=params_photo["background_opacity"])

        title = params.get("title", {})
        if title:
            draw = ImageDraw.Draw(img_card)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", title.get("font_size", params["title"]["font_size"]))
            except Exception as e:
                font = ImageFont.load_default()
            if title.get("text_outline_color", None):
                title_pos_x, title_pos_y = title.get("title_position", (20, 10))
                draw.text((title_pos_x-1, title_pos_y-1), title.get("text", ""),
                          fill=title.get("text_outline_color", "white"),
                          font=font)
                draw.text((title_pos_x+1, title_pos_y-1), title.get("text", ""),
                          fill=title.get("text_outline_color", "white"),
                          font=font)
                draw.text((title_pos_x-1, title_pos_y+1), title.get("text", ""),
                          fill=title.get("text_outline_color", "white"),
                          font=font)
                draw.text((title_pos_x+1, title_pos_y+1), title.get("text", ""),
                          fill=title.get("text_outline_color", "white"),
                          font=font)
            draw.text(title.get("title_position", (20, 10)), title.get("text", ""), fill=title.get("color", "white"),
                      font=font)

        self._add_photo(img_card, params_photo)

        text_params = params.get("text", {})
        img_card = self._draw_rectangle(img_card, text_params["frame_position"], text_params["frame_dimensions"],
                                        text_params["frame_bg_color"], text_params["frame_rounded_radius"],
                                        outline_color=text_params["frame_outline_color"],
                                        outline_width=text_params["frame_outline_width"],
                                        opacity=text_params["background_opacity"])
        self._add_card_text(img_card, text_params)

        return img_card
