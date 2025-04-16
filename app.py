import flet as ft
import time
import asyncio

def main(page: ft.Page):
    # Configuración de la ventana
    page.title = "Aplicación Flet - Título y Nota con Temporizador"
    page.window_width = 800
    page.window_height = 600
    page.padding = 20
    page.bgcolor = ft.Colors.WHITE
    
    # Variables para controlar el temporizador
    timer_running = False
    timer_paused = False
    start_time = None
    pause_time = None
    elapsed_time = 0
    
    # Variable para controlar el tamaño de la letra
    font_size_multiplier = 1.0

    # Campos de entrada para el título y la nota
    title_input = ft.TextField(label="Título", width=300, autofocus=True)
    note_input = ft.TextField(label="Nota (opcional)", width=300)
    
    # Elementos donde se mostrará el contenido
    display_title = ft.Text(
        value="", 
        size=50, 
        weight="bold", 
        text_align=ft.TextAlign.CENTER,
        selectable=False
    )
    display_note = ft.Text(
        value="", 
        size=20, 
        text_align=ft.TextAlign.CENTER,
        selectable=False
    )
    timer_text = ft.Text(
        value="00:00", 
        size=30, 
        color=ft.Colors.BLUE_700,
        weight="bold",
        selectable=False
    )

    # Contenedor que agrupa el título y la nota en forma de columna
    text_column = ft.Column(
        controls=[display_title, display_note],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    # Botón para pausar/reanudar el temporizador
    pause_resume_button = ft.IconButton(
        icon=ft.Icons.PAUSE,
        icon_color=ft.Colors.BLUE_700,
        tooltip="Pausar/Reanudar",
        on_click=lambda e: pause_resume_timer(e)
    )
    
    # Botones para ajustar el tamaño de la letra
    increase_font_button = ft.IconButton(
        icon=ft.Icons.TEXT_INCREASE,
        icon_color=ft.Colors.BLUE_700,
        tooltip="Aumentar tamaño",
        on_click=lambda e: adjust_font_size(1.1)
    )
    
    decrease_font_button = ft.IconButton(
        icon=ft.Icons.TEXT_DECREASE,
        icon_color=ft.Colors.BLUE_700,
        tooltip="Disminuir tamaño",
        on_click=lambda e: adjust_font_size(0.9)
    )
    
    # Fila para los controles del lado derecho
    controls_row = ft.Row(
        controls=[
            pause_resume_button,
            increase_font_button,
            decrease_font_button
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    # Contenedor para el temporizador
    timer_container = ft.Container(
        content=timer_text,
        alignment=ft.alignment.center,
        padding=0
    )
    
    # Contenedor para los controles
    controls_container = ft.Container(
        content=controls_row,
        alignment=ft.alignment.center,
        padding=0
    )

    # Se organiza el contenido principal en una fila
    content_row = ft.Row(
        controls=[text_column, timer_container],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    # Columna principal que contiene todo
    main_column = ft.Column(
        controls=[content_row, controls_container],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5
    )
    
    # Contenedor principal para la visualización
    display_container = ft.Container(
        content=main_column,
        expand=True,
        padding=20,
        border_radius=10,
        border=ft.border.all(2, ft.Colors.BLUE_200),
        margin=ft.margin.only(top=20)
    )

    # Función para ajustar el tamaño de la letra
    def adjust_font_size(factor):
        nonlocal font_size_multiplier
        font_size_multiplier *= factor
        
        # Limitar el rango del multiplicador para evitar tamaños extremos
        font_size_multiplier = max(0.5, min(2.0, font_size_multiplier))
        
        # Actualiza el tamaño de la letra del título, la nota y el temporizador
        base_title_size = min(80, max(40, int(page.width / 15)))
        display_title.size = base_title_size * font_size_multiplier
        display_note.size = 20 * font_size_multiplier
        
        # El temporizador tiene un factor de reducción menor para mantener mejor proporción
        timer_text.size = max(20, 30 * (0.7 + 0.3 * font_size_multiplier))
        
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
            # Reiniciar la tarea de actualización
            page.update()
            # Usar el bucle de eventos del page para crear la tarea
            page.run_task(update_display())
        
        page.update()
    
    # Función para actualizar el temporizador y aplicar el efecto arcoíris
    async def update_display():
        nonlocal start_time, elapsed_time
        # Lista de colores para el efecto arcoíris
        colors = [ft.Colors.RED, ft.Colors.ORANGE, ft.Colors.YELLOW, 
                 ft.Colors.GREEN, ft.Colors.BLUE, ft.Colors.INDIGO, ft.Colors.PURPLE]
        color_index = 0
        
        while timer_running:
            try:
                # Calcula el tiempo transcurrido
                elapsed = int(time.time() - start_time)
                elapsed_time = elapsed
                minutes, seconds = divmod(elapsed, 60)
                timer_text.value = f"{minutes:02}:{seconds:02}"
                
                # Ajusta el tamaño del título, la nota y el temporizador según el ancho de la ventana y el multiplicador
                base_title_size = min(80, max(40, int(page.width / 15)))
                display_title.size = base_title_size * font_size_multiplier
                display_note.size = 20 * font_size_multiplier
                
                # El temporizador tiene un factor de reducción menor para mantener mejor proporción
                timer_text.size = max(20, 30 * (0.7 + 0.3 * font_size_multiplier))
                
                # Aplica el efecto de cambio de color
                display_title.color = colors[color_index % len(colors)]
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
    
    # Botón para iniciar la acción
    start_button = ft.ElevatedButton(
        text="START",
        on_click=start_button_clicked,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            padding=15
        ),
        width=120
    )
    
    # Organiza los campos de entrada y el botón en una fila
    inputs_row = ft.Row(
        controls=[
            ft.Container(content=title_input, padding=5),
            ft.Container(content=note_input, padding=5),
            ft.Container(content=start_button, padding=5)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )
    
    # Contenedor para los campos de entrada
    inputs_container = ft.Container(
        content=inputs_row,
        visible=True
    )
    
    # Título de la aplicación
    app_title = ft.Text("Título y Temporizador", size=25, weight="bold", color=ft.Colors.BLUE_700)
    
    # Añade los componentes a la página
    page.add(
        app_title,
        inputs_container,
        display_container
    )
    
if __name__ == "__main__":
    ft.app(target=main)
