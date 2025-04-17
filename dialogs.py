import flet as ft
from utils import format_time

def create_settings_dialog(page, tasks, current_task_index, timer_running, timer_paused, 
                          display_title=None, display_note=None, task_position_text=None,
                          prev_task_button=None, next_task_button=None, task_list_text=None):
    """
    Crea el diálogo de configuración para ver, editar y eliminar tareas
    """
    # Crear la lista de tareas para mostrar en el diálogo
    task_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=400)
    
    # Función para cerrar el diálogo de configuración (definida antes de usarla)
    def close_settings_dialog(e=None):
        settings_dialog.open = False
        page.update()
    
    # Crear el diálogo de configuración
    settings_dialog = ft.AlertDialog(
        title=ft.Text("Configuración de Tareas"),
        content=ft.Column(
            [
                ft.Text("Lista de Tareas", style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD)),
                ft.Divider(),
                task_list_column,
            ],
            spacing=10,
            width=500,
            height=500,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: close_settings_dialog(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Función para actualizar la lista de tareas en el diálogo
    def update_task_list():
        task_list_column.controls.clear()
        
        # Si no hay tareas, mostrar un mensaje
        if len(tasks) == 0:
            task_list_column.controls.append(
                ft.Text("No hay tareas. Agrega una nueva tarea para comenzar.", italic=True)
            )
        else:
            # Agregar cada tarea a la lista
            for i, task in enumerate(tasks):
                # Obtener el tiempo formateado
                time_str = format_time(task.elapsed_time)
                
                # Crear un contenedor para la tarea
                task_container = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Tarea {i+1}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_300),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"Título: {task.title}", style=ft.TextStyle(size=16)),
                        ft.Text(f"Nota: {task.note if task.note else 'N/A'}", style=ft.TextStyle(size=14, color=ft.Colors.GREY_400)),
                        ft.Row([
                            ft.Text("Enlace: ", style=ft.TextStyle(size=14, color=ft.Colors.GREY_700)),
                            ft.TextButton(
                                text=task.link if hasattr(task, 'link') and task.link else "N/A",
                                url=task.link if hasattr(task, 'link') and task.link else None,
                                tooltip="Haz clic para abrir el enlace" if hasattr(task, 'link') and task.link else "No hay enlace disponible",
                                style=ft.ButtonStyle(
                                    color=ft.Colors.BLUE_700 if hasattr(task, 'link') and task.link else ft.Colors.GREY_400,
                                ),
                                disabled=not (hasattr(task, 'link') and task.link),
                            ),
                        ]),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar tarea",
                                on_click=lambda e, idx=i: edit_task_dialog(idx)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar tarea",
                                on_click=lambda e, idx=i: delete_task_dialog(idx)
                            ),
                        ], alignment=ft.MainAxisAlignment.END),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE),
                )
                
                task_list_column.controls.append(task_container)
        
        # Actualizar el diálogo
        page.update()
    
    # Función para editar una tarea
    def edit_task_dialog(task_index):
        # Verificar que el índice sea válido
        if task_index < 0 or task_index >= len(tasks):
            print(f"Error: Índice de tarea inválido para editar: {task_index}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Error al editar la tarea"))
            page.snack_bar.open = True
            page.update()
            return
            
        task = tasks[task_index]
        print(f"Editando tarea {task_index + 1}: {task.title}")
        
        # Crear campos de texto para el título, la nota y el enlace
        edit_title_field = ft.TextField(
            label="Título de la tarea",
            value=task.title,
            autofocus=True,
            border_radius=10,
            width=400,
        )
        
        edit_note_field = ft.TextField(
            label="Nota (opcional)",
            value=task.note,
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=10,
            width=400,
        )
        
        edit_link_field = ft.TextField(
            label="Enlace (opcional)",
            value=task.link if hasattr(task, 'link') else "",
            border_radius=10,
            width=400,
        )
        
        # Crear el diálogo de edición
        edit_dialog = ft.AlertDialog(
            modal=True,  # Hacer que el diálogo sea modal
            title=ft.Text(f"Editar Tarea {task_index + 1}"),
            content=ft.Column(
                [
                    edit_title_field,
                    edit_note_field,
                    edit_link_field,
                ],
                spacing=20,
                width=400,
                height=300,
                alignment=ft.MainAxisAlignment.START,
            )
        )
        
        # Función para guardar una tarea editada
        def save_edited_task(e):
            if not edit_title_field.value or edit_title_field.value.strip() == "":
                # Mostrar un mensaje de error si el título está vacío
                page.snack_bar = ft.SnackBar(content=ft.Text("El título de la tarea no puede estar vacío"))
                page.snack_bar.open = True
                page.update()
                return
            
            print(f"Guardando cambios en tarea {task_index + 1}")
            print(f"  Título anterior: {tasks[task_index].title}")
            print(f"  Título nuevo: {edit_title_field.value}")
            
            # Actualizar la tarea
            tasks[task_index].title = edit_title_field.value
            tasks[task_index].note = edit_note_field.value
            tasks[task_index].link = edit_link_field.value
            
            # Si la tarea actual es la que se está editando, actualizar la interfaz
            if task_index == current_task_index:
                if display_title and display_note:
                    display_title.value = edit_title_field.value
                    display_note.value = edit_note_field.value
            
            # Cerrar el diálogo de edición
            edit_dialog.open = False
            
            # Actualizar la lista de tareas
            update_task_list()
            
            # Mostrar mensaje de confirmación
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{edit_title_field.value}' actualizada correctamente"))
            page.snack_bar.open = True
            
            # Actualizar la página
            if task_list_text:
                task_list_text.value = f"Tareas agregadas: {len(tasks)}"
            
            page.update()
        
        # Función para cancelar la edición
        def cancel_edit(e):
            edit_dialog.open = False
            page.update()
        
        # Agregar botones de acción
        edit_dialog.actions = [
            ft.TextButton("Cancelar", on_click=cancel_edit),
            ft.TextButton("Guardar", on_click=save_edited_task),
        ]
        edit_dialog.actions_alignment = ft.MainAxisAlignment.END
        
        # Mostrar el diálogo de edición
        page.dialog = edit_dialog
        edit_dialog.open = True
        page.update()
    
    # Función para confirmar la eliminación de una tarea
    def delete_task_dialog(task_index):
        # Verificar que el índice sea válido
        if task_index < 0 or task_index >= len(tasks):
            print(f"Error: Índice de tarea inválido para eliminar: {task_index}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Error al eliminar la tarea"))
            page.snack_bar.open = True
            page.update()
            return
            
        task = tasks[task_index]
        print(f"Eliminando tarea {task_index + 1}: {task.title}")
        
        # Crear el diálogo de confirmación
        confirm_dialog = ft.AlertDialog(
            modal=True,  # Hacer que el diálogo sea modal
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"\u00bfEstás seguro de que deseas eliminar la tarea '{task.title}'?"),
        )
        
        # Función para cancelar la eliminación
        def cancel_delete(e):
            confirm_dialog.open = False
            page.update()
        
        # Función para confirmar la eliminación
        def confirm_delete(e):
            # Cerrar el diálogo de confirmación
            confirm_dialog.open = False
            
            # Guardar el nombre de la tarea para el mensaje de confirmación
            task_name = tasks[task_index].title
            
            print(f"Confirmando eliminación de tarea {task_index + 1}: {task_name}")
            
            # Si la tarea que se está eliminando es la actual, detener el temporizador
            if task_index == current_task_index and timer_running:
                tasks[current_task_index].timer.stop()
            
            # Eliminar la tarea
            tasks.pop(task_index)
            
            print(f"Tarea eliminada. Quedan {len(tasks)} tareas.")
            
            # Actualizar el contador de tareas
            if task_list_text:
                task_list_text.value = f"Tareas agregadas: {len(tasks)}"
            
                if current_task_index >= 0:
                    if display_title and display_note:
                        display_title.value = tasks[current_task_index].title
                        display_note.value = tasks[current_task_index].note
                    
                    # Actualizar el indicador de posición y los botones de navegación
                    if task_position_text:
                        task_position_text.value = f"Tarea {current_task_index + 1} de {len(tasks)}"
                    if prev_task_button and next_task_button:
                        prev_task_button.visible = current_task_index > 0
                        next_task_button.visible = current_task_index < len(tasks) - 1
            
            # Actualizar la lista de tareas
            update_task_list()
            page.update()
        
        # Función para cancelar la eliminación
        def cancel_delete(e):
            confirm_dialog.open = False
            page.update()
        
        # Crear el diálogo de confirmación
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Estás seguro de que deseas eliminar la tarea '{tasks[task_index].title}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_delete),
                ft.TextButton("Eliminar", on_click=delete_task),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Mostrar el diálogo de confirmación
        page.dialog = confirm_dialog
        confirm_dialog.open = True
        page.update()
    
    # Actualizar la lista de tareas
    update_task_list()
    
    # Mostrar el diálogo de configuración
    page.dialog = settings_dialog
    settings_dialog.open = True
    page.update()
    
    return settings_dialog
