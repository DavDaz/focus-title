import flet as ft
import time
import asyncio

def main(page: ft.Page):
    # Configuración de la ventana
    page.title = "Focus Title - Temporizador"
    page.window_width = 800
    page.window_height = 600
    page.padding = ft.padding.all(0)  # Eliminar padding para maximizar espacio
    page.bgcolor = "#f5f5f7"  # Color de fondo más moderno
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Configuración para que la aplicación sea responsive
    page.on_resize = lambda _: page.update()
    
    # Variables para controlar el temporizador
    timer_running = False
    timer_paused = False
    start_time = None
    pause_time = None
    elapsed_time = 0
    
    # Variable para controlar el tamaño de la letra
    font_size_multiplier = 1.0

    # Campos de entrada para el título y la nota con diseño mejorado
    title_input = ft.TextField(
        label="Título",
        autofocus=True,
        border_radius=8,
        text_size=16,
        expand=True,  # Expandir para llenar el espacio disponible
        max_length=50,  # Limitar longitud para evitar problemas de visualización
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.TITLE
    )
    
    note_input = ft.TextField(
        label="Nota (opcional)",
        border_radius=8,
        text_size=16,
        expand=True,  # Expandir para llenar el espacio disponible
        max_length=100,  # Limitar longitud para evitar problemas de visualización
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.NOTE
    )
    
    # Elementos donde se mostrará el contenido con diseño mejorado
    display_title = ft.Text(
        value="", 
        size=50, 
        weight="bold", 
        text_align=ft.TextAlign.CENTER,
        selectable=False,
        no_wrap=False,  # Permitir que el texto se ajuste
        max_lines=3,    # Limitar a 3 líneas máximo
        overflow=ft.TextOverflow.ELLIPSIS  # Mostrar ... si el texto es demasiado largo
    )
    
    display_note = ft.Text(
        value="", 
        size=20, 
        text_align=ft.TextAlign.CENTER,
        selectable=False,
        no_wrap=False,  # Permitir que el texto se ajuste
        max_lines=4,    # Limitar a 4 líneas máximo
        overflow=ft.TextOverflow.ELLIPSIS  # Mostrar ... si el texto es demasiado largo
    )
    
    timer_text = ft.Text(
        value="00:00", 
        size=30, 
        color=ft.Colors.BLUE_700,
        weight="bold",
        selectable=False,
        text_align=ft.TextAlign.CENTER
    )

    # Contenedor que agrupa el título y la nota en forma de columna con mejor diseño
    text_column = ft.Column(
        controls=[display_title, display_note],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,  # Mayor espaciado para mejor legibilidad
        tight=True   # Ajuste más compacto
    )
    
    # Botón para pausar/reanudar el temporizador con mejor diseño
    pause_resume_button = ft.IconButton(
        icon=ft.Icons.PAUSE,
        icon_color=ft.Colors.BLUE_700,
        icon_size=32,  # Botón más grande para facilitar su uso
        tooltip="Pausar/Reanudar",
        on_click=lambda e: pause_resume_timer(e)
    )
    
    # Botones para ajustar el tamaño de la letra con mejor diseño
    increase_font_button = ft.IconButton(
        icon=ft.Icons.TEXT_INCREASE,
        icon_color=ft.Colors.BLUE_700,
        icon_size=28,  # Botón más grande para facilitar su uso
        tooltip="Aumentar tamaño",
        on_click=lambda e: adjust_font_size(1.1)
    )
    
    decrease_font_button = ft.IconButton(
        icon=ft.Icons.TEXT_DECREASE,
        icon_color=ft.Colors.BLUE_700,
        icon_size=28,  # Botón más grande para facilitar su uso
        tooltip="Disminuir tamaño",
        on_click=lambda e: adjust_font_size(0.9)
    )
    
    # Botón para pantalla completa eliminado para simplificar la interfaz
    
    # Contenedor para el temporizador con mejor diseño, ahora más compacto para integrarse en la cinta de controles
    timer_container = ft.Container(
        content=timer_text,
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(horizontal=15, vertical=8),
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_200),
        width=120,
        height=50,  # Altura reducida para que coincida con los botones
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 2)
        )
    )
    
    # Fila para los controles con mejor organización, ahora incluye el temporizador
    # Se eliminaron los botones de aumentar/disminuir tamaño y pantalla completa para simplificar la interfaz
    controls_row = ft.Row(
        controls=[
            timer_container,  # Temporizador integrado en la cinta de controles
            ft.VerticalDivider(width=10, thickness=1, color=ft.Colors.BLUE_200),
            pause_resume_button
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Contenedor para los controles con mejor diseño
    controls_container = ft.Container(
        content=controls_row,
        alignment=ft.alignment.center,
        padding=10,
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_200),
        margin=ft.margin.only(top=10, bottom=10)
    )

    # Se organiza el contenido principal en una columna responsiva
    # Ahora el contenido principal solo contiene el texto, ya que el temporizador se movió a la cinta de controles
    content_layout = ft.ResponsiveRow(
        controls=[
            ft.Column(
                controls=[text_column],
                col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},  # Ahora ocupa todo el ancho
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    # Columna principal que contiene todo
    main_column = ft.Column(
        controls=[content_layout, controls_container],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    # Contenedor principal para la visualización con mejor diseño
    display_container = ft.Container(
        content=main_column,
        expand=True,
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 3)
        ),
        margin=ft.margin.only(top=20, left=10, right=10, bottom=10)
    )

    # Función para alternar pantalla completa eliminada ya que no se usa
    
    # Función para ajustar el tamaño de la letra con mejor adaptabilidad
    def adjust_font_size(factor):
        nonlocal font_size_multiplier
        font_size_multiplier *= factor
        
        # Limitar el rango del multiplicador para evitar tamaños extremos
        # Ampliamos el rango máximo para permitir textos más grandes
        font_size_multiplier = max(0.5, min(3.0, font_size_multiplier))
        
        # Actualiza el tamaño de la letra del título, la nota y el temporizador
        # Cálculo mejorado para adaptarse mejor a diferentes tamaños de pantalla
        window_width = page.width if page.width else 800
        window_height = page.height if page.height else 600
        
        # Ajuste basado en el tamaño de la ventana y la orientación
        is_landscape = window_width > window_height
        
        # Mejorado el cálculo del factor base para evitar textos demasiado pequeños
        # Establecemos un mínimo más alto para el factor base
        base_size_factor = max(0.7, min(window_width, window_height) / 800)
        
        # Calcula tamaños base adaptados al tamaño de la ventana con mínimos más altos
        base_title_size = min(90, max(40, int(window_width / (12 if is_landscape else 8))))
        base_note_size = min(40, max(20, int(window_width / 35)))
        base_timer_size = min(50, max(28, int(window_width / 22)))
        
        # Aplica el multiplicador de tamaño
        display_title.size = base_title_size * font_size_multiplier * base_size_factor
        display_note.size = base_note_size * font_size_multiplier * base_size_factor
        timer_text.size = base_timer_size * font_size_multiplier * base_size_factor
        
        # Asegurarse de que los tamaños nunca sean menores que un mínimo absoluto
        display_title.size = max(36, display_title.size)
        display_note.size = max(18, display_note.size)
        timer_text.size = max(24, timer_text.size)
        
        page.update()
    
    # Función para pausar o reanudar el temporizador
    def pause_resume_timer(e):
        nonlocal timer_running, timer_paused, pause_time, start_time, elapsed_time
        
        if not timer_running and not timer_paused:
            # Si el temporizador no está corriendo ni pausado, no hacemos nada
            return
        
        if timer_running:
            # Pausar el temporizador
            timer_running = False
            timer_paused = True
            pause_time = time.time()
            elapsed_time = int(pause_time - start_time)
            pause_resume_button.icon = ft.Icons.PLAY_ARROW
        else:
            # Reanudar el temporizador
            timer_running = True
            timer_paused = False
            start_time = time.time() - elapsed_time
            pause_resume_button.icon = ft.Icons.PAUSE
            
            # Solución mejorada para reiniciar el temporizador
            # Primero actualizamos la interfaz
            page.update()
            
            # Luego ejecutamos la función update_display directamente
            # Esto evita problemas con la creación de tareas asíncronas
            page.run_task(update_display)
        
        page.update()
    
    # Función para actualizar el temporizador y aplicar el efecto arcoíris
    async def update_display():
        nonlocal start_time, elapsed_time
        # Lista de colores para el efecto arcoíris con transiciones más suaves
        colors = [
            "#FF5252", "#FF7043", "#FFCA28", "#9CCC65", 
            "#42A5F5", "#5C6BC0", "#AB47BC", "#EC407A"
        ]
        color_index = 0
        
        while timer_running:
            try:
                # Calcula el tiempo transcurrido
                elapsed = int(time.time() - start_time)
                elapsed_time = elapsed
                minutes, seconds = divmod(elapsed, 60)
                hours, minutes = divmod(minutes, 60)
                
                # Formato del temporizador: mostrar horas solo si es necesario
                if hours > 0:
                    timer_text.value = f"{hours:02}:{minutes:02}:{seconds:02}"
                else:
                    timer_text.value = f"{minutes:02}:{seconds:02}"
                
                # Ajusta el tamaño del título, la nota y el temporizador según el tamaño de la ventana
                # y la orientación (portrait/landscape)
                window_width = page.width if page.width else 800
                window_height = page.height if page.height else 600
                
                is_landscape = window_width > window_height
                # Mejorado el cálculo del factor base para evitar textos demasiado pequeños
                base_size_factor = max(0.7, min(window_width, window_height) / 800)
                
                # Calcula tamaños base adaptados al tamaño de la ventana con mínimos más altos
                base_title_size = min(90, max(40, int(window_width / (12 if is_landscape else 8))))
                base_note_size = min(40, max(20, int(window_width / 35)))
                base_timer_size = min(50, max(28, int(window_width / 22)))
                
                # Aplica el multiplicador de tamaño
                display_title.size = base_title_size * font_size_multiplier * base_size_factor
                display_note.size = base_note_size * font_size_multiplier * base_size_factor
                timer_text.size = base_timer_size * font_size_multiplier * base_size_factor
                
                # Asegurarse de que los tamaños nunca sean menores que un mínimo absoluto
                display_title.size = max(36, display_title.size)
                display_note.size = max(18, display_note.size)
                timer_text.size = max(24, timer_text.size)
                
                # Aplica el efecto de cambio de color con transición suave
                display_title.color = colors[color_index % len(colors)]
                # Cambia también el color del borde del temporizador para un efecto visual más integrado
                timer_container.bgcolor = ft.Colors.with_opacity(0.15, colors[color_index % len(colors)])
                # También cambia el color del texto del temporizador para mejor integración visual
                timer_text.color = colors[color_index % len(colors)]
                color_index += 1
                
                # Actualiza la página
                page.update()
                
                # Espera antes de la siguiente actualización
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"Error en update_display: {e}")
                break

    # Función para manejar el clic en el botón START
    async def start_button_clicked(e):
        nonlocal timer_running, start_time, timer_paused, elapsed_time
        
        # Verifica que haya un título
        if not title_input.value:
            title_input.error_text = "Por favor ingresa un título"
            page.update()
            return
        
        # Limpia cualquier mensaje de error
        title_input.error_text = None
        
        # Asigna el contenido ingresado al título y a la nota
        display_title.value = title_input.value
        display_note.value = note_input.value
        
        # Reinicia las variables del temporizador
        start_time = time.time()
        timer_running = True
        timer_paused = False
        elapsed_time = 0
        pause_resume_button.icon = ft.Icons.PAUSE
        
        # Oculta el contenedor de inputs y el título de la aplicación
        inputs_container.visible = False
        app_title.visible = False
        
        # Ajusta el tamaño del contenedor de visualización para ocupar toda la pantalla
        display_container.margin = ft.margin.all(0)
        
        # Actualiza la página
        page.update()
        
        # Inicia la tarea de actualización
        await update_display()
    
    # Botón para iniciar la acción con mejor diseño
    start_button = ft.ElevatedButton(
        text="INICIAR",
        on_click=start_button_clicked,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation=5,
            animation_duration=300
        ),
        width=120,
        height=50,
        icon=ft.Icons.PLAY_ARROW_ROUNDED
    )
    
    # Organiza los campos de entrada y el botón en un diseño responsivo
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
                content=start_button,
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
        visible=True,
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
    
    # Añade los componentes a la página con un contenedor principal
    main_page_container = ft.Container(
        content=ft.Column(
            controls=[
                app_title,
                inputs_container,
                display_container
            ],
            spacing=0,
            expand=True
        ),
        expand=True,
        padding=0
    )
    
    page.add(main_page_container)
    
if __name__ == "__main__":
    ft.app(target=main)
