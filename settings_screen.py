import flet as ft
from utils import format_time

def create_settings_screen(page, tasks, current_task_index, timer_running, timer_paused,
                          on_edit_task, on_delete_task, on_close, deleted_tasks=None, on_restore_task=None, on_clear_deleted=None, on_export_csv=None, on_delete_selected=None):
    # Diccionario para almacenar el estado de edición de las tareas
    editing_tasks = {}
    
    # Diccionario para almacenar el estado de selección de tareas eliminadas
    selected_deleted_tasks = {}
    
    # Función para alternar el modo de edición
    def toggle_edit_mode(task_index):
        # Invertir el estado de edición para esta tarea
        editing_tasks[task_index] = not editing_tasks.get(task_index, False)
        # Actualizar la lista de tareas para reflejar el cambio
        update_task_list()
        page.update()
    
    # Función para guardar los cambios de una tarea
    def save_task_changes(task_index, title_field, note_field, link_field):
        # Verificar que el título no esté vacío
        if not title_field.value or title_field.value.strip() == "":
            page.snack_bar = ft.SnackBar(content=ft.Text("El título de la tarea no puede estar vacío"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Actualizar la tarea
        tasks[task_index].title = title_field.value
        tasks[task_index].note = note_field.value
        tasks[task_index].link = link_field.value
        
        # Guardar los cambios en la base de datos (asumimos que on_edit_task hace esto)
        on_edit_task(task_index)
        
        # Salir del modo de edición
        editing_tasks[task_index] = False
        
        # Actualizar la lista de tareas
        update_task_list()
        page.update()
        
        # Mostrar mensaje de confirmación
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{title_field.value}' actualizada correctamente"))
        page.snack_bar.open = True
        page.update()
    
    # Función para actualizar la lista de tareas
    def update_task_list():
        """
    Crea una pantalla completa de configuración en lugar de un diálogo
    """
    # Crear el contenedor principal
    settings_container = ft.Container(
        expand=True,
        padding=20,
        bgcolor=ft.Colors.WHITE,
    )
    
    # Crear el encabezado
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.BLUE_700,
                    tooltip="Volver",
                    on_click=on_close
                ),
                ft.Text(
                    "Configuración de Tareas",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        margin=ft.margin.only(bottom=20),
    )
    
    # Crear un texto para mostrar la ruta de descarga (inicialmente oculto)
    download_path_text = ft.Text(
        value="",
        size=16,
        color=ft.Colors.BLACK,
        selectable=True,  # Permite seleccionar el texto para copiarlo
        visible=False,
    )
    
    # Crear un contenedor para el mensaje de éxito al exportar CSV
    download_info_container = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_700, size=24),
                ft.Container(width=10),  # Espaciador
                download_path_text,
                ft.Container(width=10),  # Espaciador
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.BLACK,
                    tooltip="Cerrar",
                    on_click=lambda e: setattr(download_info_container, 'visible', False) or page.update(),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        padding=15,
        border=ft.border.all(2, ft.Colors.GREEN_500),
        border_radius=10,
        bgcolor="#E8F5E9",  # Color de fondo verde claro
        margin=ft.margin.only(bottom=15, top=10),
        visible=False,  # Inicialmente oculto
    )
    
    # Crear el botón de exportar a CSV con función personalizada
    def on_export_csv_click(e):
        if on_export_csv:
            # Llamar a la función original de exportación
            on_export_csv(e)
            
            # Mostrar el mensaje de éxito
            # Obtener la ruta del archivo (usando la fecha actual como aproximación)
            import datetime
            import os
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"focus_title_tareas_{timestamp}.csv"
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            filepath = os.path.join(downloads_dir, filename)
            
            # Actualizar y mostrar el contenedor de información
            download_path_text.value = f"Archivo CSV guardado en: {filepath}"
            download_path_text.visible = True
            download_info_container.visible = True
            page.update()
    
    export_csv_button = ft.Container(
        content=ft.ElevatedButton(
            text="Exportar a CSV",
            icon=ft.Icons.DOWNLOAD,
            on_click=on_export_csv_click,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
                padding=15,
            ),
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=10),
    )
    
    # Crear la lista de tareas
    task_list = ft.ListView(
        spacing=10,
        padding=10,
        expand=True,
    )
    
    # Si no hay tareas, mostrar un mensaje
    if len(tasks) == 0:
        task_list.controls.append(
            ft.Container(
                content=ft.Text(
                    "No hay tareas. Agrega una nueva tarea para comenzar.",
                    italic=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=20,
                alignment=ft.alignment.center,
            )
        )
    else:
        # Agregar cada tarea a la lista
        for i, task in enumerate(tasks):
            # Obtener el tiempo formateado
            elapsed = task.elapsed_time
            minutes, seconds = divmod(elapsed, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                time_str = f"{minutes:02}:{seconds:02}"
            
            # Verificar si la tarea está en modo edición
            is_editing = editing_tasks.get(i, False)
            
            # Contenido de la tarea según el modo (edición o visualización)
            if is_editing:
                # Crear campos para editar la tarea
                title_field = ft.TextField(
                    value=task.title,
                    label="Título",
                    border_radius=10,
                    expand=True,
                )
                
                note_field = ft.TextField(
                    value=task.note if task.note else "",
                    label="Nota",
                    multiline=True,
                    min_lines=2,
                    max_lines=3,
                    border_radius=10,
                    expand=True,
                )
                
                link_field = ft.TextField(
                    value=task.link if hasattr(task, 'link') and task.link else "",
                    label="Enlace",
                    border_radius=10,
                    expand=True,
                )
                
                # Vista de edición
                task_content = ft.Column([
                    ft.Row([
                        ft.Text(f"Tarea {i+1}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=10),  # Espaciador
                    title_field,
                    ft.Container(height=10),  # Espaciador
                    note_field,
                    ft.Container(height=10),  # Espaciador
                    link_field,
                    ft.Container(height=15),  # Espaciador
                    ft.Row([
                        ft.ElevatedButton(
                            text="Cancelar",
                            icon=ft.Icons.CANCEL,
                            on_click=lambda e, idx=i: toggle_edit_mode(idx),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.RED_700,
                            ),
                        ),
                        ft.ElevatedButton(
                            text="Guardar",
                            icon=ft.Icons.SAVE,
                            on_click=lambda e, idx=i, t=title_field, n=note_field, l=link_field: 
                                save_task_changes(idx, t, n, l),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN_700,
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.END, spacing=10),
                ])
            else:
                # Vista normal (no edición)
                task_content = ft.Column([
                    ft.Row([
                        ft.Text(f"Tarea {i+1}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Título: {task.title}", style=ft.TextStyle(size=16)),
                    ft.Text(f"Nota: {task.note if task.note else 'N/A'}", style=ft.TextStyle(size=14, color=ft.Colors.GREY_500)),
                    ft.Row([
                        ft.Text("Enlace: ", style=ft.TextStyle(size=14, color=ft.Colors.GREY_700)),
                        ft.TextButton(
                            text=task.link if hasattr(task, 'link') and task.link else "N/A",
                            url=task.link if hasattr(task, 'link') and task.link else None,
                            tooltip="Haz clic para abrir el enlace" if hasattr(task, 'link') and task.link else "No hay enlace disponible",
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLUE_700 if hasattr(task, 'link') and task.link else ft.Colors.GREY_500,
                            ),
                            disabled=not (hasattr(task, 'link') and task.link),
                        ),
                    ]),
                    ft.Row([
                        ft.ElevatedButton(
                            text="Editar",
                            icon=ft.Icons.EDIT,
                            on_click=lambda e, idx=i: on_edit_task(idx),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.BLUE_700,
                            ),
                        ),
                        ft.ElevatedButton(
                            text="Eliminar",
                            icon=ft.Icons.DELETE,
                            on_click=lambda e, idx=i: on_delete_task(idx),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.RED_700,
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.END, spacing=10),
                ])
            
            # Crear un contenedor para la tarea
            task_item = ft.Container(
                content=task_content,
                padding=15,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2)
                ),
                margin=ft.margin.only(bottom=10),
            )
            
            task_list.controls.append(task_item)
    
    # Crear el contenedor para la lista de tareas
    task_list_container = ft.Container(
        content=task_list,
        expand=True,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        padding=10,
    )
    
    # Crear la sección de tareas eliminadas si hay tareas eliminadas
    deleted_tasks_section = None
    if deleted_tasks and len(deleted_tasks) > 0:
        # Crear la lista de tareas eliminadas
        deleted_task_list = ft.ListView(
            spacing=10,
            padding=10,
            expand=True,
        )
        
        # Agregar cada tarea eliminada a la lista
        for i, task in enumerate(deleted_tasks):
            # Obtener el tiempo formateado
            elapsed = task.elapsed_time
            minutes, seconds = divmod(elapsed, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                time_str = f"{minutes:02}:{seconds:02}"
            
            # Formatear la fecha de eliminación si está disponible y convertirla de UTC a hora local
            deleted_date = 'Fecha desconocida'
            if hasattr(task, 'deleted_at') and task.deleted_at:
                try:
                    import datetime
                    # Parsear la fecha de SQLite (formato ISO)
                    utc_date = datetime.datetime.fromisoformat(task.deleted_at.replace(' ', 'T'))
                    # Convertir a hora local
                    local_date = utc_date.replace(tzinfo=datetime.timezone.utc).astimezone()
                    # Formatear la fecha en un formato legible
                    deleted_date = local_date.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(f"Error al convertir fecha en settings_screen: {e}")
                    deleted_date = task.deleted_at  # Usar la fecha original si hay error
            
            # Crear checkbox para seleccionar la tarea eliminada
            task_checkbox = ft.Checkbox(
                value=selected_deleted_tasks.get(i, False),
                on_change=lambda e, idx=i: toggle_deleted_task_selection(idx, e.control.value)
            )
            
            # Función para cambiar el estado de selección de una tarea eliminada
            def toggle_deleted_task_selection(task_idx, is_selected):
                selected_deleted_tasks[task_idx] = is_selected
                # Actualizar el botón de eliminar seleccionadas
                update_delete_selected_button()
                page.update()
            
            # Crear un contenedor para la tarea eliminada
            deleted_task_item = ft.Container(
                content=ft.Column([
                    ft.Row([
                        task_checkbox,
                        ft.Text(f"Tarea eliminada {i+1}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Título: {task.title}", style=ft.TextStyle(size=16)),
                    ft.Text(f"Nota: {task.note if task.note else 'N/A'}", style=ft.TextStyle(size=14, color=ft.Colors.GREY_500)),
                    ft.Row([
                        ft.Text("Enlace: ", style=ft.TextStyle(size=14, color=ft.Colors.GREY_700)),
                        ft.TextButton(
                            text=task.link if hasattr(task, 'link') and task.link else "N/A",
                            url=task.link if hasattr(task, 'link') and task.link else None,
                            tooltip="Haz clic para abrir el enlace" if hasattr(task, 'link') and task.link else "No hay enlace disponible",
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLUE_700 if hasattr(task, 'link') and task.link else ft.Colors.GREY_500,
                            ),
                            disabled=not (hasattr(task, 'link') and task.link),
                        ),
                    ]),
                    ft.Text(f"Eliminada: {deleted_date}", style=ft.TextStyle(size=12, color=ft.Colors.GREY_700)),
                    ft.Row([
                        ft.ElevatedButton(
                            text="Restaurar",
                            icon=ft.Icons.RESTORE,
                            on_click=lambda e, idx=i: on_restore_task(idx) if on_restore_task else None,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN_700,
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.END, spacing=10),
                ]),
                padding=15,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2)
                ),
                margin=ft.margin.only(bottom=10),
            )
            
            deleted_task_list.controls.append(deleted_task_item)
        
        # Crear el contenedor para la lista de tareas eliminadas
        deleted_task_list_container = ft.Container(
            content=deleted_task_list,
            expand=True,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=10,
        )
        
        # Crear el botón para eliminar las tareas seleccionadas
        delete_selected_button = ft.Container(
            content=ft.ElevatedButton(
                text="Eliminar seleccionadas",
                icon=ft.Icons.DELETE,
                on_click=lambda e: on_delete_selected(selected_deleted_tasks) if on_delete_selected else None,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED_500,
                    padding=15,
                ),
                disabled=True,  # Inicialmente deshabilitado hasta que se seleccione alguna tarea
            ),
            alignment=ft.alignment.center_right,
            margin=ft.margin.only(top=10, right=10),
        )
        
        # Función para actualizar el estado del botón de eliminar seleccionadas
        def update_delete_selected_button():
            # Verificar si hay alguna tarea seleccionada
            has_selected = any(selected_deleted_tasks.values())
            delete_selected_button.content.disabled = not has_selected
        
        # Crear el botón para limpiar todas las tareas eliminadas
        clear_button = ft.Container(
            content=ft.ElevatedButton(
                text="Limpiar historial",
                icon=ft.Icons.DELETE_SWEEP,
                on_click=on_clear_deleted if on_clear_deleted else None,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED_700,
                    padding=15,
                ),
            ),
            alignment=ft.alignment.center_left,
            margin=ft.margin.only(top=10, left=10),
        )
        
        # Crear un Row para contener ambos botones
        buttons_row = ft.Row(
            [clear_button, delete_selected_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Crear la sección completa de tareas eliminadas
        deleted_tasks_section = ft.Column([
            ft.Container(height=20),  # Espaciador
            ft.Text(
                "Tareas Eliminadas",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Divider(),
            deleted_task_list_container,
            buttons_row,
        ])
    
    # Columna principal con todas las secciones
    main_column = [
        header,
        download_info_container,  # Agregar el contenedor de información de descarga
        ft.Row(
            [
                ft.Text(
                    "Lista de Tareas",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                export_csv_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        ft.Divider(),
        task_list_container,
    ]
    
    # Agregar la sección de tareas eliminadas si existe
    if deleted_tasks_section:
        main_column.append(deleted_tasks_section)
    
    # Agregar el botón de cerrar
    main_column.append(
        ft.Container(
            content=ft.ElevatedButton(
                text="Cerrar",
                icon=ft.Icons.CLOSE,
                on_click=on_close,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_700,
                    padding=15,
                ),
            ),
            alignment=ft.alignment.center,
            margin=ft.margin.only(top=20),
        )
    )
    
    # Agregar todos los elementos al contenedor principal
    settings_container.content = ft.Column(
        main_column,
        spacing=10,
        expand=True,
        scroll=ft.ScrollMode.AUTO,  # Hacer que la columna sea desplazable
    )
    
    return settings_container
