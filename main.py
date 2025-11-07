from flet import *
import flet as ft  # Para compatibilidad con código existente
from borrar_duplicados import find_duplicates, delete_file
from organizar_archivos import organize_folder
from rename_files import rename_files_in_sequence
import os

def main(page):
    # Configuración básica de la ventana
    page.title = "Automatización de Tareas"
    page.window.width = 1000
    page.window.height = 700
    page.padding = 0
    page.bgcolor = ft.Colors.BLACK
    page.theme_mode = ft.ThemeMode.DARK

    # Agregar tema personalizado
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # Variables de estado
    state = {
        "current_duplicates": [],
        "current_view": "duplicates",
        "selected_folder": "",
        "organize_input_folder": "",
        "resize_input_folder": "",
        "resize_output_folder": "",
        "selecting_resize_output": False,
        "selected_files": [],
        "rename_input_folder": "",
        "rename_option": "",
        "rename_value": ""
    }

    # --- Vista funcional para archivos duplicados ---
    selected_dir_text = ft.Text(
        "No se ha seleccionado ninguna carpeta",
        size=14,
        color=ft.Colors.BLUE_200
    )
    # ListView con scroll para los duplicados
    duplicates_list = ft.ListView(
        expand=True,
        spacing=8,
        padding=0,
        auto_scroll=False,
    )
    result_text = ft.Text("", color=ft.Colors.BLUE_200)

    # Botón "Eliminar todos": invisible y deshabilitado al inicio
    delete_all_btn = ft.ElevatedButton(
        "Eliminar todos",
        icon=ft.Icons.DELETE_SWEEP_OUTLINED,
        bgcolor=ft.Colors.RED_900,
        color=ft.Colors.WHITE,
        visible=False,
        disabled=True,
    )

    def perform_delete_all(e=None):
        # Verificaciones básicas
        if not state["current_duplicates"]:
            result_text.value = "No hay duplicados para eliminar."
            result_text.color = ft.Colors.BLUE_200
            result_text.update()
            return

        # Deshabilitar el botón mientras elimina para evitar dobles clics
        delete_all_btn.disabled = True
        delete_all_btn.text = "Eliminando..."
        delete_all_btn.update()

        to_delete = [dup for dup, _ in state["current_duplicates"]]
        ok = fail = 0
        for dup in to_delete:
            try:
                if delete_file(dup):
                    ok += 1
                else:
                    fail += 1
            except Exception:
                fail += 1

        # Refrescar listado tras eliminar
        scan_and_show_duplicates()

        # Mensaje de resultado
        if fail == 0:
            result_text.value = f"Eliminados {ok} duplicados correctamente."
            result_text.color = ft.Colors.GREEN_400
        else:
            result_text.value = f"Eliminados {ok}. Fallaron {fail}."
            result_text.color = ft.Colors.ORANGE_400
        result_text.update()

        # Restaurar texto del botón según haya o no duplicados
        has_dups = bool(state["current_duplicates"])
        delete_all_btn.text = "Eliminar todos"
        delete_all_btn.disabled = not has_dups
        delete_all_btn.visible = has_dups
        delete_all_btn.update()

        # Aviso visual
        page.show_snack_bar(
            ft.SnackBar(ft.Text(result_text.value))
        )
        page.update()

    # Conectar el botón directamente a la acción (sin confirmación)
    delete_all_btn.on_click = perform_delete_all

    def scan_and_show_duplicates(e=None):
        folder = state["selected_folder"]
        if not folder or not os.path.isdir(folder):
            result_text.value = "Selecciona una carpeta válida."
            result_text.color = ft.Colors.RED_400
            result_text.update()

            # Oculta y deshabilita el botón si no hay carpeta válida
            delete_all_btn.visible = False
            delete_all_btn.disabled = True
            delete_all_btn.update()
            return

        duplicates = find_duplicates(folder)
        state["current_duplicates"] = duplicates

        duplicates_list.controls.clear()
        if not duplicates:
            result_text.value = "No se encontraron archivos duplicados."
            result_text.color = ft.Colors.GREEN_400
        else:
            result_text.value = f"Se encontraron {len(duplicates)} archivos duplicados."
            result_text.color = ft.Colors.ORANGE_400
            for dup, orig in duplicates:
                def make_delete_fn(dup_file):
                    return lambda _ev: delete_and_refresh(dup_file)
                # Cada ítem de la lista
                item = ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CONTENT_COPY_OUTLINED, color=ft.Colors.BLUE_200, size=18),
                            ft.Text(
                                f"Duplicado: {dup}\nOriginal: {orig}",
                                color=ft.Colors.BLUE_200,
                                expand=True,
                                no_wrap=False,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar este duplicado",
                                icon_color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.RED_900,
                                on_click=make_delete_fn(dup),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    padding=8,
                    border_radius=6,
                    bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
                )
                duplicates_list.controls.append(item)

        duplicates_list.update()
        result_text.update()

        # Mostrar y habilitar el botón si hay duplicados; ocultarlo si no
        has_dups = bool(state["current_duplicates"])
        delete_all_btn.visible = has_dups
        delete_all_btn.disabled = not has_dups
        delete_all_btn.update()

    def delete_and_refresh(dup_file):
        if delete_file(dup_file):
            state["current_duplicates"] = [item for item in state["current_duplicates"] if item[0] != dup_file]
            scan_and_show_duplicates()
        else:
            result_text.value = f"Error al eliminar: {dup_file}"
            result_text.color = ft.Colors.RED_400
            result_text.update()

    def handle_folder_picker(e: ft.FilePickerResultEvent):
        if e.path:
            state["selected_folder"] = e.path
            selected_dir_text.value = f"Carpeta seleccionada: {e.path}"
            selected_dir_text.update()
            scan_and_show_duplicates()

    folder_picker = ft.FilePicker(on_result=handle_folder_picker)
    page.overlay.append(folder_picker)

    duplicate_files_view = ft.Container(
        content=ft.Column([
            ft.Text("Eliminar Archivos Duplicados", color=ft.Colors.BLUE_200, size=24),
            ft.Row([
                ft.ElevatedButton(
                    "Seleccionar carpeta",
                    icon=ft.Icons.FOLDER_OPEN_OUTLINED,
                    on_click=lambda _ev: folder_picker.get_directory_path()
                ),
                selected_dir_text,
                delete_all_btn,  # Botón de eliminación masiva
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            result_text,
            ft.Divider(),
            duplicates_list  # ListView con scroll
        ], expand=True),  # importante para permitir que el ListView se expanda y scrollee
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
        padding=20,
        border_radius=8,
    )

    # --- Vista: Organizar archivos ---
    organize_selected_text = ft.Text("No se ha seleccionado ninguna carpeta", color=ft.Colors.BLUE_200)
    organize_result_text = ft.Text("", color=ft.Colors.BLUE_200)

    def handle_organize_folder_picker(e: ft.FilePickerResultEvent):
        if e.path:
            state["organize_input_folder"] = e.path
            organize_selected_text.value = f"Carpeta a organizar: {e.path}"
            organize_selected_text.update()

    def run_organize(_ev=None):
        folder = state.get("organize_input_folder") or ""
        if not folder or not os.path.isdir(folder):
            organize_result_text.value = "Selecciona una carpeta válida para organizar."
            organize_result_text.color = ft.Colors.RED_400
            organize_result_text.update()
            return
        try:
            # Ejecutar organización
            organize_folder(folder)
            organize_result_text.value = "Organización completada."
            organize_result_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            organize_result_text.value = f"Error al organizar: {ex}"
            organize_result_text.color = ft.Colors.RED_400
        organize_result_text.update()
        page.show_snack_bar(
            ft.SnackBar(ft.Text(organize_result_text.value))
        )
        page.update()

    organize_picker = ft.FilePicker(on_result=handle_organize_folder_picker)
    page.overlay.append(organize_picker)

    organize_files_view = ft.Container(
        content=ft.Column(
            [
                ft.Text("Organizar archivos por tipo", color=ft.Colors.BLUE_200, size=24),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Seleccionar carpeta",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=lambda _ev: organize_picker.get_directory_path(),
                        ),
                        organize_selected_text,
                        ft.ElevatedButton(
                            "Organizar",
                            icon=ft.Icons.CLEANING_SERVICES,
                            bgcolor=ft.Colors.BLUE_800,
                            color=ft.Colors.WHITE,
                            on_click=run_organize,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                ft.Divider(),
                organize_result_text,
                ft.Text(
                    "Moverá imágenes, videos, documentos, datasets y comprimidos a subcarpetas.",
                    color=ft.Colors.BLUE_200,
                    size=12,
                ),
            ],
            expand=True,
        ),
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
        padding=20,
        border_radius=8,
    )

    # --- Vista: Redimensionar imágenes ---
    resize_input_text = ft.Text("No se ha seleccionado carpeta de entrada", color=ft.Colors.BLUE_200)
    resize_output_text = ft.Text("No se ha seleccionado carpeta de salida", color=ft.Colors.BLUE_200)
    resize_result_text = ft.Text("", color=ft.Colors.BLUE_200)
    
    # Campos para las dimensiones
    width_field = ft.TextField(
        label="Ancho",
        value="800",
        width=100,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        color=ft.Colors.BLUE_200,
        border_color=ft.Colors.BLUE_200,
    )
    height_field = ft.TextField(
        label="Alto",
        value="600",
        width=100,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        color=ft.Colors.BLUE_200,
        border_color=ft.Colors.BLUE_200,
    )

    def handle_resize_input_picker(e: ft.FilePickerResultEvent):
        if e.path:
            state["resize_input_folder"] = e.path
            resize_input_text.value = f"Carpeta de entrada: {e.path}"
            resize_input_text.update()

    def handle_resize_output_picker(e: ft.FilePickerResultEvent):
        if e.path:
            state["resize_output_folder"] = e.path
            resize_output_text.value = f"Carpeta de salida: {e.path}"
            resize_output_text.update()

    def run_resize(_):
        input_folder = state.get("resize_input_folder", "")
        output_folder = state.get("resize_output_folder", "")
        
        # Validaciones
        if not input_folder or not os.path.isdir(input_folder):
            resize_result_text.value = "Selecciona una carpeta de entrada válida"
            resize_result_text.color = ft.Colors.RED_400
            resize_result_text.update()
            return
            
        if not output_folder or not os.path.isdir(output_folder):
            resize_result_text.value = "Selecciona una carpeta de salida válida"
            resize_result_text.color = ft.Colors.RED_400
            resize_result_text.update()
            return
            
        try:
            width = int(width_field.value)
            height = int(height_field.value)
            
            if width <= 0 or height <= 0:
                raise ValueError("Las dimensiones deben ser positivas")
                
            from cambiar_tamaño import batch_resize
            batch_resize(input_folder, output_folder, width, height)
            
            resize_result_text.value = "Imágenes redimensionadas exitosamente"
            resize_result_text.color = ft.Colors.GREEN_400
            
        except ValueError as e:
            resize_result_text.value = f"Error en las dimensiones: {str(e)}"
            resize_result_text.color = ft.Colors.RED_400
        except Exception as e:
            resize_result_text.value = f"Error al redimensionar: {str(e)}"
            resize_result_text.color = ft.Colors.RED_400
            
        resize_result_text.update()

    resize_input_picker = ft.FilePicker(on_result=handle_resize_input_picker)
    resize_output_picker = ft.FilePicker(on_result=handle_resize_output_picker)
    page.overlay.extend([resize_input_picker, resize_output_picker])

    resize_files_view = ft.Container(
        content=ft.Column([
            ft.Text("Redimensionar Imágenes", color=ft.Colors.BLUE_200, size=24),
            
            # Selector de carpeta de entrada
            ft.Row([
                ft.ElevatedButton(
                    "Seleccionar carpeta de entrada",
                    icon=ft.Icons.FOLDER_OPEN_OUTLINED,
                    on_click=lambda _: resize_input_picker.get_directory_path()
                ),
                resize_input_text,
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            
            # Selector de carpeta de salida
            ft.Row([
                ft.ElevatedButton(
                    "Seleccionar carpeta de salida",
                    icon=ft.Icons.FOLDER_OPEN_OUTLINED,
                    on_click=lambda _: resize_output_picker.get_directory_path()
                ),
                resize_output_text,
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            
            ft.Divider(),
            
            # Campos de dimensiones
            ft.Row([
                width_field,
                ft.Text("×", color=ft.Colors.BLUE_200),
                height_field,
                ft.Text("píxeles", color=ft.Colors.BLUE_200),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            
            # Botón de redimensionar
            ft.ElevatedButton(
                "Redimensionar imágenes",
                icon=ft.Icons.PHOTO_SIZE_SELECT_LARGE,
                on_click=run_resize,
                bgcolor=ft.Colors.BLUE_800,
                color=ft.Colors.WHITE,
            ),
            
            ft.Divider(),
            resize_result_text,
            
            ft.Text(
                "Las imágenes redimensionadas se guardarán con el prefijo 'resized_'",
                color=ft.Colors.BLUE_200,
                size=12,
            ),
        ], expand=True),
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
        padding=20,
        border_radius=8,
    )
    convert_images_view = ft.Container(
        content=ft.Text("Vista: Convertir imágenes", color=ft.Colors.BLUE_200), expand=True
    )
    extract_audio_view = ft.Container(
        content=ft.Text("Vista: Extraer audio", color=ft.Colors.BLUE_200), expand=True
    )
    merge_pdfs_view = ft.Container(
        content=ft.Text("Vista: Fusionar PDFs", color=ft.Colors.BLUE_200), expand=True
    )
    # --- Vista: Renombrar archivos ---
    rename_selected_text = ft.Text("No se han seleccionado archivos", color=ft.Colors.BLUE_200)
    rename_result_text = ft.Text("", color=ft.Colors.BLUE_200)
    rename_base_name = ft.TextField(
        label="Nombre base",
        hint_text="Ej: Factura julio",
        border_color=ft.Colors.BLUE_200,
        color=ft.Colors.BLUE_200,
        width=300
    )
    selected_files_list = ft.ListView(
        expand=True,
        spacing=8,
        padding=0,
        auto_scroll=False,
    )

    def handle_files_selected(e: ft.FilePickerResultEvent):
        if not e.files:
            return
            
        # Guardar los archivos seleccionados
        state["selected_files"] = [f.path for f in e.files]
        
        # Actualizar texto y lista de archivos
        rename_selected_text.value = f"Archivos seleccionados: {len(e.files)}"
        
        # Limpiar y actualizar la lista de archivos
        selected_files_list.controls.clear()
        for file in e.files:
            item = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.FILE_PRESENT, color=ft.Colors.BLUE_200, size=18),
                        ft.Text(file.name, color=ft.Colors.BLUE_200, expand=True),
                    ]
                ),
                padding=8,
                border_radius=6,
                bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
            )
            selected_files_list.controls.append(item)
            
        rename_selected_text.update()
        selected_files_list.update()

    def run_rename(e):
        if not state.get("selected_files"):
            rename_result_text.value = "Por favor, selecciona archivos primero."
            rename_result_text.color = ft.Colors.RED_400
            rename_result_text.update()
            return
            
        if not rename_base_name.value:
            rename_result_text.value = "Por favor, ingresa un nombre base."
            rename_result_text.color = ft.Colors.RED_400
            rename_result_text.update()
            return
            
        try:
            results = rename_files_in_sequence(state["selected_files"], rename_base_name.value)
            
            # Contar éxitos y fallos
            successes = sum(1 for success, _, _ in results if success)
            failures = sum(1 for success, _, _ in results if not success)
            
            if failures == 0:
                rename_result_text.value = f"Se renombraron {successes} archivos exitosamente."
                rename_result_text.color = ft.Colors.GREEN_400
            else:
                rename_result_text.value = f"Se renombraron {successes} archivos. {failures} fallaron."
                rename_result_text.color = ft.Colors.ORANGE_400
                
            # Limpiar la lista y el estado después de renombrar
            selected_files_list.controls.clear()
            state["selected_files"] = []
            rename_selected_text.value = "No se han seleccionado archivos"
            rename_base_name.value = ""
            
            # Actualizar todo
            rename_result_text.update()
            selected_files_list.update()
            rename_selected_text.update()
            rename_base_name.update()
            
        except Exception as ex:
            rename_result_text.value = f"Error al renombrar: {str(ex)}"
            rename_result_text.color = ft.Colors.RED_400
            rename_result_text.update()

    file_picker = ft.FilePicker(
        on_result=handle_files_selected
    )
    page.overlay.append(file_picker)

    rename_files_view = ft.Container(
        content=ft.Column([
            ft.Text("Renombrar Archivos en Serie", color=ft.Colors.BLUE_200, size=24),
            ft.Row([
                ft.ElevatedButton(
                    "Seleccionar archivos",
                    icon=ft.Icons.FILE_UPLOAD,
                    on_click=lambda _: file_picker.pick_files(
                        allow_multiple=True
                    )
                ),
                rename_selected_text,
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            ft.Divider(),
            rename_base_name,
            ft.ElevatedButton(
                "Renombrar archivos",
                icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
                on_click=run_rename,
                bgcolor=ft.Colors.BLUE_800,
                color=ft.Colors.WHITE,
            ),
            rename_result_text,
            ft.Divider(),
            selected_files_list,
        ], expand=True),
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
        padding=20,
        border_radius=8,
    )

    # El área de contenido principal inicia con la vista de duplicados
    content_area = ft.Container(content=duplicate_files_view, expand=True, padding=10)

    def change_view(e):
        selected = e.control.selected_index
        if selected == 0:
            state["current_view"] = "duplicates"
            content_area.content = duplicate_files_view
        elif selected == 1:
            state["current_view"] = "organize"
            content_area.content = organize_files_view
        elif selected == 2:
            state["current_view"] = "resize"
            content_area.content = resize_files_view
        elif selected == 3:
            state["current_view"] = "rename"
            content_area.content = rename_files_view
        content_area.update()

    # Menú lateral
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.FIND_IN_PAGE_OUTLINED,
                selected_icon=ft.Icons.FIND_IN_PAGE,
                label="Duplicados",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.AUTO_AWESOME_MOTION_OUTLINED,
                selected_icon=ft.Icons.AUTO_AWESOME_MOTION,
                label="Organizar",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CROP_OUTLINED,
                selected_icon=ft.Icons.CROP,
                label="Redimensionar",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
                selected_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
                label="Renombrar",
            ),
        ],
        on_change=change_view,
        bgcolor=ft.Colors.with_opacity(0.45, ft.Colors.GREY_900),
    )

    # --- Fondo con imagen repetida usando Stack + Image ---
    background_image = ft.Image(
        src="fondo.jpg",
        fit=ft.ImageFit.NONE,
        repeat=ft.ImageRepeat.REPEAT,
        opacity=1.0,
        gapless_playback=True,
        expand=True,
    )

    main_content = ft.Row(
        [
            rail,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            content_area,
        ],
        expand=True,
    )

    # Superponer el contenido encima del fondo
    root = ft.Stack(
        controls=[
            background_image,
            main_content,
        ],
        expand=True,
    )

    # --- Agrega el layout principal ---
    page.add(root)

if __name__ == "__main__":
    # Asegúrate de tener la carpeta "assets" con tu imagen "fondo.jpg"
    ft.app(target=main, assets_dir="assets")