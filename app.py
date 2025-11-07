(jnkm,
Colors.BLUE,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # Variables de estado
    state = {
        "current_duplicates": [],
        "current_view": "duplicates",
        "selected_folder": "",
        "resize_input_folder": "",
        "resize_output_folder": "",
        "selecting_resize_output": False,
        "convert_input_file": "",
        "audio_input_folder": "",
        "audio_extraction_progress": 0,
        "total_videos": 0,
        "current_video": "",
        "pdf_input_folder": "",
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
    duplicates_list = ft.Column([])
    result_text = ft.Text("", color=ft.Colors.BLUE_200)

    # Botón "Eliminar todos" (visible siempre, pero deshabilitado si no hay duplicados)
    delete_all_btn = ft.ElevatedButton(
        "Eliminar todos",
        icon=ft.Icons.DELETE_SWEEP,
        bgcolor=ft.Colors.RED_900,
        color=ft.Colors.WHITE,
        disabled=True,  # se habilita tras el escaneo si hay duplicados
    )

    # Diálogo de confirmación
    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Eliminar todos los duplicados"),
        content=ft.Text(""),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def perform_delete_all():
        if not state["current_duplicates"]:
            result_text.value = "No hay duplicados para eliminar."
            result_text.color = ft.Colors.BLUE_200
            result_text.update()
            return

        # Deshabilitar el botón mientras se elimina para evitar doble clic
        delete_all_btn.disabled = True
        delete_all_btn.update()

        to_delete = [dup for dup, _ in state["current_duplicates"]]
        ok = 0
        fail = 0
        for dup in to_delete:
            try:
                if delete_file(dup):
                    ok += 1
                else:
                    fail += 1
            except Exception:
                fail += 1

        # Refresca la lista tras eliminar
        scan_and_show_duplicates()
        # Muestra resultado
        if fail == 0:
            result_text.value = f"Eliminados {ok} duplicados correctamente."
            result_text.color = ft.Colors.GREEN_400
        else:
            result_text.value = f"Eliminados {ok}. Fallaron {fail}."
            result_text.color = ft.Colors.ORANGE_400
        result_text.update()

        # Aviso visual
        page.snack_bar = ft.SnackBar(ft.Text(result_text.value), open=True)
        page.update()

    def confirm_delete_all(e):
        confirm_dialog.open = False
        page.update()
        perform_delete_all()

    def cancel_delete_all(e):
        confirm_dialog.open = False
        page.update()

    def open_confirm_delete_all(e):
        if not state["current_duplicates"]:
            result_text.value = "No hay duplicados para eliminar."
            result_text.color = ft.Colors.BLUE_200
            result_text.update()
            return
        count = len(state["current_duplicates"])
        confirm_dialog.title = ft.Text("Eliminar todos los duplicados")
        confirm_dialog.content = ft.Text(
            f"Se eliminarán {count} archivos duplicados.\nEsta acción no se puede deshacer.\n¿Deseas continuar?"
        )
        confirm_dialog.actions = [
            ft.TextButton("Cancelar", on_click=cancel_delete_all),
            ft.ElevatedButton(
                "Eliminar",
                icon=ft.Icons.DELETE_FOREVER,
                bgcolor=ft.Colors.RED_900,
                color=ft.Colors.WHITE,
                on_click=confirm_delete_all,
            ),
        ]
        page.dialog = confirm_dialog
        confirm_dialog.open = True
        page.update()

    # Asignar handler al botón (después de definir la función)
    delete_all_btn.on_click = open_confirm_delete_all

    def scan_and_show_duplicates(e=None):
        folder = state["selected_folder"]
        if not folder or not os.path.isdir(folder):
            result_text.value = "Selecciona una carpeta válida."
            result_text.color = ft.Colors.RED_400
            result_text.update()
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
                    return lambda e: delete_and_refresh(dup_file)
                duplicates_list.controls.append(
                    ft.Row([
                        ft.Text(f"Duplicado: {dup}\nOriginal: {orig}", color=ft.Colors.BLUE_200, expand=True),
                        ft.ElevatedButton(
                            "Eliminar",
                            icon=ft.Icons.DELETE,
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.RED_900,
                            on_click=make_delete_fn(dup)
                        )
                    ])
                )
        duplicates_list.update()
        result_text.update()

        # Habilita/deshabilita el botón "Eliminar todos"
        delete_all_btn.disabled = not bool(state["current_duplicates"])
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
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=lambda e: folder_picker.get_directory_path()
                ),
                selected_dir_text,
                delete_all_btn,  # Botón agregado
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            result_text,
            ft.Divider(),
            duplicates_list
        ]),
        expand=True,
        # Fondo semitransparente para mejorar legibilidad sobre la imagen
        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
        padding=20,
        border_radius=8,
    )

    # --- Definición de vistas mínimas para evitar errores ---
    organize_files_view = ft.Container(
        content=ft.Text("Vista: Organizar archivos", color=ft.Colors.BLUE_200), expand=True
    )
    resize_files_view = ft.Container(
        content=ft.Text("Vista: Redimensionar imágenes", color=ft.Colors.BLUE_200), expand=True
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
    rename_files_view = ft.Container(
        content=ft.Text("Vista: Renombrar archivos", color=ft.Colors.BLUE_200), expand=True
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
            state["current_view"] = "convert"
            content_area.content = convert_images_view
        elif selected == 4:
            state["current_view"] = "audio"
            content_area.content = extract_audio_view
        elif selected == 5:
            state["current_view"] = "merge_pdfs"
            content_area.content = merge_pdfs_view
        elif selected == 6:
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
                icon=ft.Icons.DELETE_FOREVER,
                selected_icon=ft.Icons.DELETE_FOREVER,
                label="Duplicados",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FOLDER_COPY,
                selected_icon=ft.Icons.FOLDER_COPY,
                label="Organizar",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PHOTO_SIZE_SELECT_LARGE,
                selected_icon=ft.Icons.PHOTO_SIZE_SELECT_LARGE,
                label="Redimensionar",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TRANSFORM,
                selected_icon=ft.Icons.TRANSFORM,
                label="Convertir",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.AUDIOTRACK,
                selected_icon=ft.Icons.AUDIOTRACK,
                label="Extraer Audio",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MERGE_TYPE,
                selected_icon=ft.Icons.MERGE_TYPE,
                label="Fusionar PDFs",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.EDIT,
                selected_icon=ft.Icons.EDIT,
                label="Renombrar",
            ),
        ],
        on_change=change_view,
        bgcolor=ft.Colors.with_opacity(0.45, ft.Colors.GREY_900),
    )

    # --- Fondo con imagen repetida usando Stack + Image ---
    background_image = ft.Image(
        src="fondo.jpg",                  # coloca tu imagen en assets/fondo.jpg
        fit=ft.ImageFit.NONE,             # no escalar; usar tamaño natural
        repeat=ft.ImageRepeat.REPEAT,     # repetir en ambas direcciones (mosaico)
        opacity=1.0,
        gapless_playback=True,
        expand=True,                      # ocupar todo el espacio del Stack
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