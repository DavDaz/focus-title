import flet as ft
from utils import format_time

def create_settings_screen(page, tasks, current_task_index, timer_running, timer_paused,
                          on_edit_task, on_delete_task, on_close):
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
            
            # Crear un contenedor para la tarea
            task_item = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Tarea {i+1}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Título: {task.title}", style=ft.TextStyle(size=16)),
                    ft.Text(f"Nota: {task.note if task.note else 'N/A'}", style=ft.TextStyle(size=14, color=ft.Colors.GREY_500)),
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
            
            task_list.controls.append(task_item)
    
    # Crear el contenedor para la lista de tareas
    task_list_container = ft.Container(
        content=task_list,
        expand=True,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        padding=10,
    )
    
    # Agregar todos los elementos al contenedor principal
    settings_container.content = ft.Column(
        [
            header,
            ft.Text(
                "Lista de Tareas",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Divider(),
            task_list_container,
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
            ),
        ],
        spacing=10,
        expand=True,
    )
    
    return settings_container
