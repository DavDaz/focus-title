import flet as ft
from utils import format_time, create_button

def create_task_display(title, note, timer_text, task_position_text):
    """
    Crea el componente de visualización de tareas
    """
    # Título de la tarea con estilo mejorado
    display_title = ft.Text(
        value=title,
        size=60,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLACK,
        text_align=ft.TextAlign.CENTER,
        no_wrap=False,
    )
    
    # Nota de la tarea con estilo mejorado
    display_note = ft.Text(
        value=note,
        size=24,
        italic=True,
        color=ft.Colors.BLACK87,
        text_align=ft.TextAlign.CENTER,
        no_wrap=False,
    )
    
    # Contenedor para el temporizador con borde y sombra
    timer_container = ft.Container(
        content=timer_text,
        padding=20,
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_300),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 3)
        ),
    )
    
    # Botones de navegación entre tareas
    prev_task_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color=ft.Colors.BLUE_700,
        tooltip="Tarea anterior",
        icon_size=30,
        visible=False,  # Inicialmente invisible hasta que haya más de una tarea
    )
    
    next_task_button = ft.IconButton(
        icon=ft.Icons.ARROW_FORWARD,
        icon_color=ft.Colors.BLUE_700,
        tooltip="Siguiente tarea",
        icon_size=30,
        visible=False,  # Inicialmente invisible hasta que haya más de una tarea
    )
    
    # Botón de pausa/reanudación
    pause_resume_button = ft.IconButton(
        icon=ft.Icons.PAUSE,
        icon_color=ft.Colors.BLUE_700,
        tooltip="Pausar/Reanudar",
        icon_size=30,
    )
    
    # Botón para volver a la pantalla de inicio
    home_button = ft.IconButton(
        icon=ft.Icons.HOME,
        icon_color=ft.Colors.BLUE_700,
        tooltip="Volver al inicio",
        icon_size=30,
    )
    
    # Contenedor para los botones de control
    control_buttons = ft.Row(
        [prev_task_button, pause_resume_button, home_button, next_task_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )
    
    # Contenedor principal para la visualización de la tarea
    task_display = ft.Container(
        content=ft.Column(
            [
                task_position_text,
                display_title,
                display_note,
                timer_container,
                control_buttons,
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
        border_radius=20,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 5)
        ),
        margin=10,
    )
    
    return {
        "container": task_display,
        "title": display_title,
        "note": display_note,
        "timer_container": timer_container,
        "prev_button": prev_task_button,
        "next_button": next_task_button,
        "pause_resume_button": pause_resume_button,
        "home_button": home_button,
    }

def create_welcome_screen(title_input, note_input, add_task_button, start_button, settings_button, task_list_text):
    """
    Crea la pantalla de bienvenida con campos para agregar tareas
    """
    # Título de la aplicación con mejor diseño
    app_title = ft.Container(
        content=ft.Text(
            "Focus Title",
            size=30,
            weight="bold",
            color=ft.Colors.BLUE_700,
            text_align=ft.TextAlign.CENTER
        ),
        margin=ft.margin.only(top=20, bottom=10),
        alignment=ft.alignment.center
    )
    
    # Organiza los campos de entrada y los botones en un diseño responsivo
    inputs_layout = ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=title_input,
                padding=10,
                col={"xs": 12, "sm": 12, "md": 5, "lg": 5, "xl": 5}
            ),
            ft.Container(
                content=note_input,
                padding=10,
                col={"xs": 12, "sm": 12, "md": 5, "lg": 5, "xl": 5}
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        add_task_button,
                        task_list_text
                    ],
                    spacing=5,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=10,
                alignment=ft.alignment.center,
                col={"xs": 12, "sm": 12, "md": 5, "lg": 5, "xl": 5}
            ),
            ft.Container(
                content=start_button,
                padding=10,
                alignment=ft.alignment.center,
                col={"xs": 12, "sm": 12, "md": 2, "lg": 2, "xl": 2}
            ),
            ft.Container(
                content=settings_button,
                padding=10,
                alignment=ft.alignment.center,
                col={"xs": 12, "sm": 12, "md": 2, "lg": 2, "xl": 2}
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Contenedor para los campos de entrada con mejor diseño
    inputs_container = ft.Container(
        content=inputs_layout,
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 3)
        ),
        margin=ft.margin.only(top=10, left=10, right=10, bottom=10)
    )
    
    # Contenedor principal para la pantalla de bienvenida
    welcome_container = ft.Container(
        content=ft.Column(
            [
                app_title,
                inputs_container,
            ],
            spacing=0,
            expand=True
        ),
        expand=True,
        padding=0
    )
    
    return welcome_container

def create_input_fields():
    """
    Crea los campos de entrada para el título y la nota
    """
    # Campo de entrada para el título
    title_input = ft.TextField(
        label="Título",
        autofocus=True,
        border_radius=8,
        text_size=16,
        expand=True,
        max_length=50,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.TITLE
    )
    
    # Campo de entrada para la nota
    note_input = ft.TextField(
        label="Nota (opcional)",
        border_radius=8,
        text_size=16,
        expand=True,
        max_length=100,
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.NOTE
    )
    
    return title_input, note_input
