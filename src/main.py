import os
import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import filedialog

import flet as ft
from PIL import Image as PILImage, ImageOps, UnidentifiedImageError

try:
    from core.analyzer import ImageAnalyzer
except ImportError:
    from src.core.analyzer import ImageAnalyzer


analyzer = ImageAnalyzer()


def build_thumbnail_bytes(image_path: Path, size: tuple[int, int] = (180, 180)) -> bytes | None:
    try:
        with PILImage.open(image_path) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
            image.thumbnail(size)
            output = BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()
    except (UnidentifiedImageError, OSError, ValueError):
        return None


def main(page: ft.Page):
    page.title = "CopyCat Finder"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    page.add(
        ft.Text("Welcome to CopyCat Finder!", size=30, weight=ft.FontWeight.BOLD),
        ft.Text("This application helps you find and manage your duplicate images.", italic=True),
        ft.Divider(),
    )

    results_area = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def on_pick_folder(e):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        picked_path = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Choose Folder to Scan",
        )
        root.destroy()

        if not picked_path:
            page.update()
            return

        results_area.controls.clear()
        results_area.controls.append(ft.Text("Scanning for similar images...", italic=True))
        page.update()

        groups = analyzer.find_duplicates(picked_path, threshold=0.92)

        results_area.controls.clear()
        if not groups:
            results_area.controls.append(ft.Text("No duplicate or highly similar images found."))
            page.update()
            return

        results_area.controls.append(ft.Text(f"Found {len(groups)} groups of similar images."))
        for index, group in enumerate(groups, start=1):
            group_column = ft.Column()
            group_column.controls.append(ft.Text(f"Group {index}", weight=ft.FontWeight.BOLD))
            for image_path in group:
                path = Path(image_path)
                thumbnail_bytes = build_thumbnail_bytes(path)
                image_preview = ft.Image(
                    src=thumbnail_bytes or "https://placehold.co/180x180/png?text=Preview",
                    width=180,
                    height=180,
                    border_radius=8,
                    fit=ft.BoxFit.CONTAIN,
                )
                keep_checkbox = ft.Checkbox(label="Keep", value=True)
                preview_container = ft.Container(
                    content=image_preview,
                    width=180,
                    height=180,
                    border_radius=8,
                )
                card_column = ft.Column(
                    [
                        preview_container,
                        ft.Text(path.name, size=12, selectable=True),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                group_column.controls.append(
                    ft.Row([keep_checkbox, card_column], spacing=10, vertical_alignment=ft.MainAxisAlignment.START)
                )
            results_area.controls.append(group_column)

        page.update()

    page.add(
        ft.Row([
            ft.Button("Choose Folder", on_click=on_pick_folder),
        ]),
        results_area,
    )


if __name__ == "__main__":
    ft.run(main)