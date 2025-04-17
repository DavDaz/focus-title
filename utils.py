import flet as ft

def format_time(elapsed_seconds):
    """
    Formatea el tiempo en segundos a un formato legible (minutos:segundos o horas:minutos:segundos)
    """
    minutes, seconds = divmod(elapsed_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"

def calculate_font_sizes(page, font_size_multiplier=1.0):
    """
    Calcula los tamaños de fuente óptimos basados en el tamaño de la ventana
    """
    window_width = page.width if page.width else 800
    window_height = page.height if page.height else 600
    
    is_landscape = window_width > window_height
    base_size_factor = max(0.7, min(window_width, window_height) / 800)
    
    # Calcula tamaños base adaptados al tamaño de la ventana con mínimos más altos
    base_title_size = min(90, max(40, int(window_width / (12 if is_landscape else 8))))
    base_note_size = min(40, max(20, int(window_width / 35)))
    base_timer_size = min(50, max(28, int(window_width / 22)))
    
    # Aplica el multiplicador de tamaño
    title_size = max(36, base_title_size * font_size_multiplier * base_size_factor)
    note_size = max(18, base_note_size * font_size_multiplier * base_size_factor)
    timer_size = max(24, base_timer_size * font_size_multiplier * base_size_factor)
    
    return {
        "title": title_size,
        "note": note_size,
        "timer": timer_size
    }

def create_button(text, icon, on_click, color=ft.Colors.BLUE_700, width=150, height=50):
    """
    Crea un botón con estilo consistente
    """
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=color,
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation=5,
            animation_duration=300
        ),
        width=width,
        height=height
    )
