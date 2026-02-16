from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
from tkinter import filedialog


class PrintablePDFBuilder:
    def __init__(
        self,
        image_dir: Path,
        page_size=A4,
        printer_margin_mm: float = 10.0,
        photo_width_mm: float = 60.0
    ):
        self.image_dir = Path(image_dir)
        self.page_size = page_size

        # Conversion mm → points
        self.printer_margin = printer_margin_mm * mm
        self.photo_width = photo_width_mm * mm

        self.images = self._load_images()
        if not self.images:
            raise ValueError("No image found in directory")

        self.photo_ratio = self._compute_ratio()
        self.photo_height = self.photo_width / self.photo_ratio


    def _load_images(self):
        return sorted(
            list(self.image_dir.glob("*.jpg")) +
            list(self.image_dir.glob("*.jpeg")) +
            list(self.image_dir.glob("*.png"))
        )

    def _compute_ratio(self):
        with Image.open(self.images[0]) as img:
            w, h = img.size
        return w / h


    def _compute_layout(self):
        page_width, page_height = self.page_size

        usable_width = page_width - 2 * self.printer_margin
        usable_height = page_height - 2 * self.printer_margin

        cols = int(usable_width // self.photo_width)
        rows = int(usable_height // self.photo_height)

        if cols == 0 or rows == 0:
            raise ValueError("Picture too big to be printed")

        photos_per_page = cols * rows

        return cols, rows, photos_per_page

    def generate_pdf(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if not save_path:
            return

        c = canvas.Canvas(save_path, pagesize=self.page_size)

        cols, rows, per_page = self._compute_layout()

        start_x = self.printer_margin
        start_y = self.page_size[1] - self.printer_margin - self.photo_height

        for index, img_path in enumerate(self.images):
            page_index = index % per_page

            if page_index == 0 and index != 0:
                c.showPage()

            col = page_index % cols
            row = page_index // cols

            x = start_x + col * self.photo_width
            y = start_y - row * self.photo_height

            c.drawImage(
                str(img_path),
                x,
                y,
                width=self.photo_width,
                height=self.photo_height,
                preserveAspectRatio=True,
                anchor='c'
            )

        c.save()
