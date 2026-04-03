import flet as ft

def main(page: ft.Page):
    page.title = "CopyCat Finder"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    page.add(
        ft.Text("Welcome to CopyCat Finder!", size=30, weight=ft.FontWeight.BOLD),
        ft.Text("This application helps you find and manage your copycat files.", italic=True),
        ft.Divider()
    )

    # En plats där vi senare visar resultaten
    results_area = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def on_pick_folder(e: ft.FilePickerResultEvent):
        if e.path:
            page.snackbar = ft.Snackbar(ft.Text(f"Vald mapp: {e.path}"))
            page.snackbar.open = True
            # Här kommer vi senare anropa vår AI-funktion för att hitta copycat-filer i den valda mappen
            page.update()

    file_picker = ft.FilePicker(on_result=on_pick_folder)
    page.overlay.append(file_picker)

    page.add(
        ft.ElevatedButton("Välj mapp att skanna",
                          icon=ft.icons.FOLDER_OPEN,
                          on_click=lambda _: file_picker.get_directory_path()),
        results_area
    )

if __name__ == "__main__":
    ft.app(target=main)