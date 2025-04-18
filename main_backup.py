import flet as ft
import asyncio
import csv
import os
import datetime
from models import Task, TaskFactory, TimerState
from utils import format_time, calculate_font_sizes, create_button
from ui_components import create_task_display, create_welcome_screen, create_input_fields
from settings_screen import create_settings_screen
from dialogs import create_settings_dialog

def main(page: ft.Page):
    # ConfiguraciÃ³n inicial de la pÃ¡gina
    page.title = "Focus Title - Temporizador"
    page.window_width = 800
    page.window_height = 600
    page.padding = ft.padding.all(0)  # Eliminar padding para maximizar espacio
    page.bgcolor = "#f5f5f7"  # Color de fondo mÃ¡s moderno
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # ConfiguraciÃ³n para que la aplicaciÃ³n sea responsive
    page.on_resize = lambda _: page.update()
    
    # Variables para controlar el temporizador
    timer_running = False
    timer_paused = False
    
    # Variable para controlar el tamaÃ±o de la letra
    font_size_multiplier = 1.0
    
    # Lista de tareas
    tasks = []
    current_task_index = 0
    
    # Crear campos de entrada para el tÃ­tulo, la nota y el enlace
    title_input, note_input = create_input_fields()
    
    # Campo de entrada para el enlace
    link_input = ft.TextField(
        label="Enlace (opcional)",
        border_radius=8,
        text_size=16,
        expand=True,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.LINK
    )
    
    # Crear el texto del temporizador
    timer_text = ft.Text(
        value="00:00",
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER,
    )
    
    # Crear el texto de posiciÃ³n de la tarea
    task_position_text = ft.Text(
        value="",
        size=14,
        color=ft.Colors.GREY_700,
        text_align=ft.TextAlign.CENTER,
    )
    
    # Crear el texto para mostrar la cantidad de tareas
    task_list_text = ft.Text(
        value="Tareas agregadas: 0",
        size=14,
        color=ft.Colors.GREY_700,
        text_align=ft.TextAlign.CENTER
    )
    
    # Crear componentes de visualizaciÃ³n de tareas
    task_components = create_task_display("", "", timer_text, task_position_text, "")
    display_title = task_components["title"]
    display_note = task_components["note"]
    display_link = task_components["link"]
    timer_container = task_components["timer_container"]
    prev_task_button = task_components["prev_button"]
    next_task_button = task_components["next_button"]
    pause_resume_button = task_components["pause_resume_button"]
    home_button = task_components["home_button"]
    task_container = task_components["container"]
    
    # FunciÃ³n para ajustar el tamaÃ±o de la fuente
    def adjust_font_size(factor):
        nonlocal font_size_multiplier
        font_size_multiplier = max(0.5, min(2.0, font_size_multiplier * factor))
        
        # Calcular nuevos tamaÃ±os
        sizes = calculate_font_sizes(page, font_size_multiplier)
        
        # Aplicar nuevos tamaÃ±os
        display_title.size = sizes["title"]
        display_note.size = sizes["note"]
        timer_text.size = sizes["timer"]
        
        # Actualizar la pÃ¡gina
        page.update()
    
    # FunciÃ³n para pausar o reanudar el temporizador
    def pause_resume_timer(e):
        nonlocal timer_running, timer_paused
        
        # Obtener la tarea actual
        current_task = tasks[current_task_index]
        
        # Si el temporizador estÃ¡ detenido, iniciÃ©moslo
        if current_task.timer.state == TimerState.STOPPED:
            current_task.timer.start()
            timer_running = True
            timer_paused = False
            pause_resume_button.icon = ft.Icons.PAUSE
            page.update()
            page.run_task(update_display)
            return
        
        if current_task.timer.state == TimerState.RUNNING:
            # Pausar el temporizador
            current_task.timer.pause()
            timer_running = False
            timer_paused = True
            pause_resume_button.icon = ft.Icons.PLAY_ARROW
        else:  # PAUSED
            # Reanudar el temporizador
            current_task.timer.resume()
            timer_running = True
            timer_paused = False
            pause_resume_button.icon = ft.Icons.PAUSE
            
            # Actualizar la interfaz
            page.update()
            
            # Luego ejecutamos la funciÃ³n update_display directamente usando page.run_task
            page.run_task(update_display)
        
        page.update()
    
    # FunciÃ³n para actualizar el temporizador y aplicar el efecto arcoÃ­ris
    async def update_display():
        nonlocal timer_running
        # Lista de colores para el efecto arcoÃ­ris con transiciones mÃ¡s suaves
        colors = [
            "#FF5252", "#FF7043", "#FFCA28", "#9CCC65", 
            "#42A5F5", "#5C6BC0", "#AB47BC", "#EC407A"
        ]
        color_index = 0
        last_second = -1  # Para controlar la actualizaciÃ³n por segundo
        
        print("Iniciando temporizador...")
        
        # Obtener la tarea actual
        current_task = tasks[current_task_index]
        
        # Asegurarse de que el temporizador estÃ© corriendo
        if current_task.timer.state != TimerState.RUNNING:
            current_task.timer.start()
        
        timer_running = True
        
        # Verificar que estamos trabajando con la tarea actual
        task_index_at_start = current_task_index
        
        while timer_running and current_task_index == task_index_at_start and current_task.timer.state == TimerState.RUNNING:
            try:
                # Verificar si el temporizador sigue corriendo o si hemos cambiado de tarea
                if current_task.timer.state != TimerState.RUNNING or current_task_index != task_index_at_start:
                    break
                    
                # Obtener el tiempo transcurrido de la tarea actual
                elapsed = current_task.elapsed_time
                current_second = elapsed
                
                # Actualizar solo cuando cambie el segundo
                if current_second != last_second:
                    last_second = current_second
                    
                    # Actualizar el texto del temporizador
                    timer_text.value = format_time(elapsed)
                    
                    # Aplica el efecto de cambio de color con transiciÃ³n suave
                    # Solo cambiar el color cada 5 segundos para un efecto mÃ¡s suave
                    if elapsed % 5 == 0:
                        display_title.color = colors[color_index % len(colors)]
                        # Cambia tambiÃ©n el color del borde del temporizador para un efecto visual mÃ¡s integrado
                        timer_container.bgcolor = ft.Colors.with_opacity(0.15, colors[color_index % len(colors)])
                        # TambiÃ©n cambia el color del texto del temporizador para mejor integraciÃ³n visual
                        timer_text.color = colors[color_index % len(colors)]
                        color_index += 1
                    
                    # Actualiza la pÃ¡gina
                    page.update()
                
                # Ajusta el tamaÃ±o del tÃ­tulo, la nota y el temporizador segÃºn el tamaÃ±o de la ventana
                # y la orientaciÃ³n (portrait/landscape) - esto se hace menos frecuentemente
                if elapsed % 5 == 0:
                    sizes = calculate_font_sizes(page, font_size_multiplier)
                    display_title.size = sizes["title"]
                    display_note.size = sizes["note"]
                    timer_text.size = sizes["timer"]
                
                # Espera un tiempo mÃ¡s corto para actualizar mÃ¡s frecuentemente
                # Esto permite una actualizaciÃ³n mÃ¡s fluida del temporizador
                await asyncio.sleep(0.1)  # Actualizar cada 100ms para mayor fluidez
            except Exception as e:
                print(f"Error en update_display: {e}")
                break
        
        print("Temporizador detenido")
    
    # FunciÃ³n para agregar una tarea a la lista
    def add_task_to_list():
        nonlocal tasks
        
        # Verificar que haya un tÃ­tulo
        if not title_input.value or title_input.value.strip() == "":
            # Mostrar mensaje de error
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor ingresa un tÃ­tulo para la tarea"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Crear una nueva tarea
        new_task = TaskFactory.create_task(title_input.value, note_input.value, link_input.value)
        tasks.append(new_task)
        
        # Limpiar los campos de entrada
        title_input.value = ""
        note_input.value = ""
        link_input.value = ""
        
        # Actualizar el contador de tareas
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Habilitar el botÃ³n de inicio si es la primera tarea
        if len(tasks) == 1:
            start_button.disabled = False
        
        # Actualizar la lista de tareas si la pantalla de configuraciÃ³n estÃ¡ visible
        if config_container.visible:
            update_task_list()
        
        # Mostrar mensaje de confirmaciÃ³n
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{new_task.title}' agregada correctamente"))
        page.snack_bar.open = True
        
        page.update()
    
    # FunciÃ³n para mostrar la pantalla de configuraciÃ³n
    def show_settings_screen(e=None):
        # Ocultar las pantallas actuales
        welcome_container.visible = False
        task_container.visible = False
        
        # Mostrar la pantalla de configuraciÃ³n
        config_container.visible = True
        
        # Actualizar la lista de tareas en la pantalla de configuraciÃ³n
        update_task_list()
        
        page.update()
    
    # FunciÃ³n para cerrar la pantalla de configuraciÃ³n
    def close_settings_screen(e=None):
        # Ocultar la pantalla de configuraciÃ³n
        config_container.visible = False
        
        # Mostrar la pantalla de inicio
        welcome_container.visible = True
        task_container.visible = False
        
        # Actualizar el contador de tareas
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Habilitar o deshabilitar el botÃ³n de inicio segÃºn si hay tareas
        start_button.disabled = len(tasks) == 0
        
        page.update()
    
    # FunciÃ³n para editar una tarea (ahora solo se usa como respaldo)
    def edit_task(task_index):
        nonlocal current_task_index
        
        # Verificar que el Ã­ndice sea vÃ¡lido
        if task_index < 0 or task_index >= len(tasks):
            print(f"Error: Ãndice de tarea invÃ¡lido para editar: {task_index}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Error al editar la tarea"))
            page.snack_bar.open = True
            page.update()
            return
        
        print(f"Editando tarea {task_index + 1}: {tasks[task_index].title}")
        
        # Actualizar la lista de tareas para mostrar los campos de ediciÃ³n
        update_task_list()
    
    # FunciÃ³n para eliminar una tarea
    def delete_task(task_index):
        nonlocal current_task_index, timer_running, timer_paused
        
        # Verificar que el Ã­ndice sea vÃ¡lido
        if task_index < 0 or task_index >= len(tasks):
            print(f"Error: Ãndice de tarea invÃ¡lido para eliminar: {task_index}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Error al eliminar la tarea"))
            page.snack_bar.open = True
            page.update()
            return
        
        print(f"Eliminando tarea {task_index + 1}: {tasks[task_index].title}")
        
        # Guardar el nombre de la tarea para el mensaje de confirmaciÃ³n
        task_name = tasks[task_index].title
        
        # Si la tarea que se estÃ¡ eliminando es la actual, detener el temporizador
        if task_index == current_task_index:
            tasks[current_task_index].timer.stop()
            timer_running = False
            timer_paused = False
        
        # Eliminar la tarea
        tasks.pop(task_index)
        
        print(f"Tarea eliminada. Quedan {len(tasks)} tareas.")
        
        # Actualizar el contador de tareas
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Si no hay tareas, deshabilitar el botÃ³n de inicio
        if len(tasks) == 0:
            start_button.disabled = True
        else:
            # Ajustar el Ã­ndice de la tarea actual si es necesario
            if current_task_index >= len(tasks):
                current_task_index = len(tasks) - 1
            elif current_task_index > task_index:
                current_task_index -= 1
            
            # Actualizar la interfaz con la tarea actual si estamos en la pantalla de tareas
            if not config_container.visible and current_task_index >= 0:
                display_title.value = tasks[current_task_index].title
                display_note.value = tasks[current_task_index].note
                
                # Actualizar el indicador de posiciÃ³n y los botones de navegaciÃ³n
                task_position_text.value = f"Tarea {current_task_index + 1} de {len(tasks)}"
                prev_task_button.visible = current_task_index > 0
                next_task_button.visible = current_task_index < len(tasks) - 1
        
        # Mostrar mensaje de confirmaciÃ³n
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{task_name}' eliminada correctamente"))
        page.snack_bar.open = True
        
        # Actualizar la lista de tareas
        update_task_list()
        page.update()
    
    # Esta funciÃ³n ya no se usa, pero la mantenemos por compatibilidad
    def confirm_delete_task(task_index, dialog):
        # Cerrar el diÃ¡logo de confirmaciÃ³n
        dialog.open = False
        page.update()
    
    # FunciÃ³n para actualizar la lista de tareas en la pantalla de configuraciÃ³n
    def update_task_list():
        # Limpiar la lista de tareas
        task_list.controls.clear()
        
        print(f"Actualizando lista de tareas. Total: {len(tasks)}")
        
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
                task_container = create_task_item(i, task, time_str)
                task_list.controls.append(task_container)
                
                print(f"  Agregando tarea {i+1} a la lista: {task.title}")
        
        # Actualizar el contador de tareas en la pantalla principal
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Habilitar o deshabilitar el botÃ³n de inicio segÃºn si hay tareas
        start_button.disabled = len(tasks) == 0
        
        page.update()
    
    # FunciÃ³n para crear un elemento de tarea con ediciÃ³n in-line
    def create_task_item(index, task, time_str):
        # Crear un contenedor para la vista normal (no ediciÃ³n)
        normal_view = ft.Column([
            ft.Row([
                ft.Text(f"Tarea {index+1}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(f"TÃ­tulo: {task.title}", style=ft.TextStyle(size=16)),
            ft.Text(f"Nota: {task.note if task.note else 'N/A'}", style=ft.TextStyle(size=14, color=ft.Colors.GREY_500)),
            ft.Row([
                ft.ElevatedButton(
                    text="Editar",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e, idx=index: toggle_edit_mode(idx),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_700,
                    ),
                ),
                ft.ElevatedButton(
                    text="Eliminar",
                    icon=ft.Icons.DELETE,
                    on_click=lambda e, idx=index: delete_task(idx),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
        ])
        
        # Crear campos para la vista de ediciÃ³n
        edit_title_field = ft.TextField(
            value=task.title,
            label="TÃ­tulo",
            border_radius=10,
            width=400,
        )
        
        edit_note_field = ft.TextField(
            value=task.note if task.note else "",
            label="Nota",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=10,
            width=400,
        )
        
        # Crear un contenedor para la vista de ediciÃ³n
        edit_view = ft.Column([
            ft.Row([
                ft.Text(f"Editando Tarea {index+1}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            edit_title_field,
            edit_note_field,
            ft.Row([
                ft.ElevatedButton(
                    text="Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e, idx=index, tf=edit_title_field, nf=edit_note_field: save_task_changes(idx, tf, nf),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_700,
                    ),
                ),
                ft.ElevatedButton(
                    text="Cancelar",
                    icon=ft.Icons.CANCEL,
                    on_click=lambda e, idx=index: toggle_edit_mode(idx, cancel=True),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREY_700,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
        ])
        
        # Crear un contenedor para la tarea que puede alternar entre vistas
        edit_view.visible = False  # Inicialmente oculto
        
        task_container = ft.Container(
            content=ft.Stack([
                normal_view,
                edit_view,
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
            data={"normal_view": normal_view, "edit_view": edit_view, "index": index}  # Guardar referencias para acceso fÃ¡cil
        )
        
        return task_container
    
    # FunciÃ³n para alternar entre modo de visualizaciÃ³n y ediciÃ³n
    def toggle_edit_mode(task_index, cancel=False):
        # Buscar el contenedor de la tarea por su Ã­ndice
        for task_container in task_list.controls:
            if hasattr(task_container, "data") and task_container.data.get("index") == task_index:
                normal_view = task_container.data["normal_view"]
                edit_view = task_container.data["edit_view"]
                
                # Alternar la visibilidad de las vistas
                normal_view.visible = not normal_view.visible
                edit_view.visible = not edit_view.visible
                
                # Si estamos cancelando, no hacemos nada mÃ¡s
                if not cancel and edit_view.visible:
                    # Estamos entrando en modo de ediciÃ³n
                    print(f"Editando tarea {task_index + 1}: {tasks[task_index].title}")
                
                page.update()
                break
    
    # FunciÃ³n para guardar los cambios en una tarea
    def save_task_changes(task_index, title_field, note_field):
        # Verificar que el tÃ­tulo no estÃ© vacÃ­o
        if not title_field.value or title_field.value.strip() == "":
            page.snack_bar = ft.SnackBar(content=ft.Text("El tÃ­tulo de la tarea no puede estar vacÃ­o"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Guardar el tÃ­tulo anterior para el mensaje de confirmaciÃ³n
        old_title = tasks[task_index].title
        
        print(f"Guardando cambios en tarea {task_index + 1}")
        print(f"  TÃ­tulo anterior: {old_title}")
        print(f"  TÃ­tulo nuevo: {title_field.value}")
        
        # Actualizar la tarea
        tasks[task_index].title = title_field.value
        tasks[task_index].note = note_field.value
        
        # Si la tarea actual es la que se estÃ¡ editando, actualizar la interfaz principal
        if task_index == current_task_index:
            display_title.value = title_field.value
            display_note.value = note_field.value
        
        # Volver al modo de visualizaciÃ³n
        toggle_edit_mode(task_index)
        
        # Actualizar la lista de tareas para reflejar los cambios
        update_task_list()
        
        # Mostrar mensaje de confirmaciÃ³n
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{title_field.value}' actualizada correctamente"))
        page.snack_bar.open = True
        
        page.update()
    
    # FunciÃ³n para exportar tareas a CSV
    def export_tasks_to_csv():
        # Verificar si hay tareas para exportar
        if len(tasks) == 0:
            page.snack_bar = ft.SnackBar(content=ft.Text("No hay tareas para exportar"))
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            # Crear el directorio de descargas si no existe
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            
            # Crear un nombre de archivo con timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"focus_title_tareas_{timestamp}.csv"
            filepath = os.path.join(downloads_dir, filename)
            
            # Abrir el archivo para escribir
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Crear el escritor CSV
                csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                
                # Escribir encabezados sin tildes
                csv_writer.writerow(["Tarea", "Titulo", "Nota", "Tiempo (segundos)", "Tiempo (formato)"])
                
                # Escribir datos de cada tarea
                for i, task in enumerate(tasks):
                    # Manejar comillas dobles en tÃ­tulo y nota
                    title = task.title.replace('"', "'")
                    note = task.note.replace('"', "'") if task.note else ""
                    
                    # Obtener el tiempo formateado
                    time_str = format_time(task.elapsed_time)
                    
                    # Escribir fila
                    csv_writer.writerow([i+1, title, note, task.elapsed_time, time_str])
            
            # Mostrar mensaje de Ã©xito en snackbar
            page.snack_bar = ft.SnackBar(content=ft.Text("Archivo CSV exportado exitosamente"))
            page.snack_bar.open = True
            
            # Mostrar la ruta de descarga en el contenedor de informaciÃ³n
            set_download_info_visible(True, filepath)
            
            print(f"Archivo CSV exportado exitosamente a: {filepath}")
            
        except Exception as e:
            # Mostrar mensaje de error
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al exportar tareas: {str(e)}"))
            page.snack_bar.open = True
            page.update()
            print(f"Error al exportar tareas a CSV: {str(e)}")
    
    # FunciÃ³n para regresar a la pantalla de inicio
    def return_to_home():
        nonlocal timer_running, timer_paused
        
        # Si hay una tarea activa, pausar su temporizador
        if current_task_index >= 0 and current_task_index < len(tasks):
            current_task = tasks[current_task_index]
            if current_task.timer.state == TimerState.RUNNING:
                current_task.timer.pause()
                timer_running = False
                timer_paused = True
        
        # Mostrar la pantalla de inicio y ocultar la pantalla de tareas
        welcome_container.visible = True
        task_container.visible = False
        
        # Actualizar la pÃ¡gina
        page.update()
    
    # FunciÃ³n para navegar entre tareas
    def navigate_task(direction):
        nonlocal current_task_index, timer_running, timer_paused
        
        # Obtener la tarea actual
        current_task = tasks[current_task_index]
        
        # Pausar el temporizador de la tarea actual si estÃ¡ corriendo
        if current_task.timer.state == TimerState.RUNNING:
            current_task.timer.pause()
            timer_running = False
            timer_paused = True
        
        # Calcular el nuevo Ã­ndice
        new_index = current_task_index + direction
        
        # Verificar que el Ã­ndice estÃ© dentro de los lÃ­mites
        if 0 <= new_index < len(tasks):
            current_task_index = new_index
            
            # Obtener la nueva tarea actual
            new_current_task = tasks[current_task_index]
            
            # Cargar la tarea actual
            display_title.value = new_current_task.title
            display_note.value = new_current_task.note
            
            # Establecer el tiempo guardado para esta tarea
            elapsed_time = new_current_task.elapsed_time
            
            # Actualizar el texto del temporizador
            timer_text.value = format_time(elapsed_time)
            
            # Actualizar el indicador de posiciÃ³n
            task_position_text.value = f"Tarea {current_task_index + 1} de {len(tasks)}"
            
            # Actualizar visibilidad de los botones de navegaciÃ³n
            prev_task_button.visible = current_task_index > 0
            next_task_button.visible = current_task_index < len(tasks) - 1
            
            # Actualizar el botÃ³n de pausa/reanudaciÃ³n segÃºn el estado de la nueva tarea
            if new_current_task.timer.state == TimerState.RUNNING:
                pause_resume_button.icon = ft.Icons.PAUSE
                timer_running = True
                timer_paused = False
            else:  # PAUSED o STOPPED
                pause_resume_button.icon = ft.Icons.PLAY_ARROW
                timer_running = False
                timer_paused = (new_current_task.timer.state == TimerState.PAUSED)
        
        # Actualizar la pÃ¡gina
        page.update()
    
    # FunciÃ³n para iniciar el temporizador desde la pantalla de inicio
    def start_button_clicked(e):
        nonlocal current_task_index, timer_running, timer_paused
        
        # Verificar que haya al menos una tarea
        if len(tasks) == 0:
            page.snack_bar = ft.SnackBar(content=ft.Text("Agrega al menos una tarea antes de iniciar"))
            page.snack_bar.open = True
            page.update()
            return
        
        print("Iniciando temporizador desde start_button_clicked")
        
        # Establecer la primera tarea como la actual
        current_task_index = 0
        
        # Obtener la tarea actual
        current_task = tasks[current_task_index]
        
        # Cargar la tarea actual
        display_title.value = current_task.title
        display_note.value = current_task.note
        
        # Establecer el tiempo guardado para esta tarea
        elapsed_time = current_task.elapsed_time
        timer_text.value = format_time(elapsed_time)
        
        # Actualizar el indicador de posiciÃ³n
        task_position_text.value = f"Tarea {current_task_index + 1} de {len(tasks)}"
        
        # Actualizar visibilidad de los botones de navegaciÃ³n
        prev_task_button.visible = current_task_index > 0
        next_task_button.visible = current_task_index < len(tasks) - 1
        
        # Iniciar el temporizador
        current_task.timer.start()
        timer_running = True
        timer_paused = False
        pause_resume_button.icon = ft.Icons.PAUSE
        
        # Mostrar la pantalla de tareas y ocultar la pantalla de inicio
        welcome_container.visible = False
        task_container.visible = True
        
        # Actualizar la pÃ¡gina
        page.update()
        
        # Iniciar la actualizaciÃ³n del temporizador
        page.run_task(update_display)
    
    # Crear botones para la pantalla de inicio
    start_button = create_button(
        text="INICIAR",
        icon=ft.Icons.PLAY_ARROW,
        on_click=start_button_clicked,
        color=ft.Colors.GREEN_700
    )
    
    # Deshabilitar el botÃ³n de inicio si no hay tareas
    start_button.disabled = True
    
    add_task_button = create_button(
        text="AGREGAR TAREA",
        icon=ft.Icons.ADD_TASK,
        on_click=lambda e: add_task_to_list(),
        color=ft.Colors.GREEN_700
    )
    
    settings_button = create_button(
        text="CONFIGURACIÃ“N",
        icon=ft.Icons.SETTINGS,
        on_click=show_settings_screen,
        color=ft.Colors.BLUE_700
    )
    
    # Configurar eventos para los botones de navegaciÃ³n y control
    prev_task_button.on_click = lambda e: navigate_task(-1)
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.BLUE_700,
                    tooltip="Volver",
                    on_click=close_settings_screen
                ),
                ft.Text(
                    "ConfiguraciÃ³n de Tareas",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.ElevatedButton(
                    text="Exportar a CSV",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: export_tasks_to_csv(),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_700,
                    ),
                    tooltip="Exportar lista de tareas a archivo CSV",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        margin=ft.margin.only(bottom=20),
    )
    
    # Lista de tareas
    task_list = ft.ListView(
        spacing=10,
        padding=10,
        expand=True,
    )
    
    # Contenedor para la lista de tareas
    task_list_container = ft.Container(
        content=task_list,
        expand=True,
    )
    
    # Crear un texto para mostrar la ruta de descarga (inicialmente vacÃ­o)
    download_path_text = ft.Text(
        value="",
        size=16,
        color=ft.Colors.BLACK,  # Cambiado a negro para mejor visibilidad
        selectable=True,  # Permite seleccionar el texto para copiarlo
    )
    
    # Crear un contenedor para el texto de descarga con un botÃ³n para cerrarlo
    download_info_container = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_700, size=24),
                ft.Container(width=10),  # Espaciador
                download_path_text,
                ft.Container(width=10),  # Espaciador
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.BLACK,  # Cambiado a negro para mejor visibilidad
                    tooltip="Cerrar",
                    on_click=lambda e: set_download_info_visible(False),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,  # Espacio entre elementos
        ),
        padding=15,  # Padding aumentado
        border=ft.border.all(2, ft.Colors.GREEN_500),  # Borde mÃ¡s visible
        border_radius=10,
        bgcolor="#E8F5E9",  # Color de fondo verde claro
        margin=ft.margin.only(bottom=15, top=10),  # MÃ¡s espacio
        visible=False,  # Inicialmente oculto
    )
    
    # FunciÃ³n para mostrar u ocultar la informaciÃ³n de descarga
    def set_download_info_visible(visible, path=""):
        download_info_container.visible = visible
        if visible and path:
            download_path_text.value = f"Archivo CSV guardado en: {path}"
            # Asegurarse de que el texto sea visible
            download_path_text.visible = True
        page.update()
    
    # Crear una columna para la pantalla de configuraciÃ³n
    settings_screen = ft.Column(
        [
            header,
            download_info_container,  # Agregar el contenedor de informaciÃ³n de descarga
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Lista de Tareas", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                        ft.Divider(),

                        task_list_container,
                    ],
                    spacing=10,
                ),
                padding=10,
                expand=True,
            ),
        ],
        expand=True,
    )
    
    # Contenedor principal para la pantalla de configuraciÃ³n
    config_container = ft.Container(
        content=settings_screen,
        expand=True,
        padding=20,
        bgcolor=ft.Colors.WHITE,
        visible=False
    )
    
    # Inicialmente, mostrar la pantalla de bienvenida y ocultar las demÃ¡s
    welcome_container.visible = True
    task_container.visible = False
    config_container.visible = False
    
    # AÃ±adir los contenedores a la pÃ¡gina
    page.add(
        ft.Container(
            content=ft.Stack([welcome_container, task_container, config_container]),
            expand=True,
            padding=0
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
