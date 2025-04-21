import flet as ft
import asyncio
import csv
import os
import datetime
import time
import atexit  # Para asegurar guardado robusto al cerrar la app
from models import Task, TaskFactory, TimerState
from utils import format_time, calculate_font_sizes, create_button
from ui_components import create_task_display, create_welcome_screen, create_input_fields
from settings_screen import create_settings_screen
from dialogs import create_settings_dialog
from database import Database

def main(page: ft.Page):
    # Configuración inicial de la página
    page.title = "Focus Title - Temporizador"
    page.window_width = 800
    page.window_height = 600
    page.padding = ft.padding.all(0)  # Eliminar padding para maximizar espacio
    page.bgcolor = "#f5f5f7"  # Color de fondo más moderno
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Configuración para que la aplicación sea responsive
    page.on_resize = lambda _: page.update()
    
    # Inicializar la base de datos
    db = Database()
    
    # Función para guardar todas las tareas periódicamente
    async def save_tasks_periodically():
        while True:
            await asyncio.sleep(60)  # Guardar cada minuto
            try:
                print("Guardando tareas periódicamente...")
                db.save_all_tasks(tasks)
            except Exception as e:
                print(f"Error al guardar tareas periódicamente: {e}")
    
    # Iniciar el guardado periódico
    page.run_task(save_tasks_periodically)
    
    # Función para guardar tareas cuando la página se cierra
    def save_all_and_close():
        print("Guardando todas las tareas y cerrando la base de datos...")
        try:
            # Pausar todos los temporizadores activos y actualizar tiempos
            for task in tasks:
                if hasattr(task, 'timer') and task.timer.state == TimerState.RUNNING:
                    task.timer.pause()
                    print(f"Temporizador de '{task.title}' pausado con tiempo acumulado: {task.elapsed_time} segundos")
            db.save_all_tasks(tasks)
            db.close()
            print("Tareas guardadas correctamente al cerrar la aplicación")
        except Exception as e:
            print(f"Error al guardar tareas al cerrar: {e}")

    def on_window_event(e):
        if e.data == "close":
            print("Ventana cerrando, guardando tareas...")
            save_all_and_close()
    
    # Registrar el evento de cierre de ventana
    page.on_window_event = on_window_event

    # Registrar el handler con atexit para asegurar guardado aunque falle el evento de ventana
    atexit.register(save_all_and_close)

    
    # Variables para controlar el temporizador
    timer_running = False
    timer_paused = False
    
    # Variable para controlar el tamaño de la letra
    font_size_multiplier = 1.0
    
    # Lista de tareas
    tasks = db.load_tasks()  # Cargar tareas desde la base de datos
    current_task_index = 0 if len(tasks) > 0 else -1
    
    # Variable para controlar si ya se actualizó la lista de tareas
    tasks_list_updated = False
    
    # Crear campos de entrada para el título, la nota y el enlace
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
    
    # Crear el texto de posición de la tarea
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
    
    # Crear componentes de visualización de tareas
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
    
    # Función para ajustar el tamaño de la fuente
    def adjust_font_size(factor):
        nonlocal font_size_multiplier
        font_size_multiplier = max(0.5, min(2.0, font_size_multiplier * factor))
        
        # Calcular nuevos tamaños
        sizes = calculate_font_sizes(page, font_size_multiplier)
        
        # Aplicar nuevos tamaños
        display_title.size = sizes["title"]
        display_note.size = sizes["note"]
        timer_text.size = sizes["timer"]
        
        # Actualizar la página
        page.update()
    
    # Función para pausar o reanudar el temporizador
    def pause_resume_timer(e):
        nonlocal timer_running, timer_paused
        
        # Obtener la tarea actual
        current_task = tasks[current_task_index]
        
        # Si el temporizador está detenido, iniciémoslo
        if current_task.timer.state == TimerState.STOPPED:
            # Guardar el tiempo acumulado actual
            saved_time = current_task.elapsed_time
            print(f"Iniciando tarea con tiempo acumulado: {saved_time} segundos")
            
            # En lugar de usar start() que reinicia el tiempo, vamos a establecer manualmente el estado
            # y calcular el tiempo de inicio para que el tiempo acumulado se mantenga
            current_task.timer.state = TimerState.RUNNING
            current_task.timer.start_time = time.time() - saved_time
            
            # Actualizar el texto del temporizador para mostrar el tiempo acumulado
            timer_text.value = format_time(saved_time)
            
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
            
            # Luego ejecutamos la función update_display directamente usando page.run_task
            page.run_task(update_display)
        
        page.update()
    
    # Función para actualizar el temporizador y aplicar el efecto arcoíris
    async def update_display():
        nonlocal timer_running
        # Lista de colores para el efecto arcoíris con transiciones más suaves
        colors = [
            "#FF5252", "#FF7043", "#FFCA28", "#9CCC65", 
            "#42A5F5", "#5C6BC0", "#AB47BC", "#EC407A"
        ]
        color_index = 0
        last_second = -1  # Para controlar la actualización por segundo
        
        print("Iniciando temporizador...")
        
        # Obtener la tarea actual
        current_task = tasks[current_task_index]
        
        # Asegurarse de que el temporizador esté corriendo
        if current_task.timer.state != TimerState.RUNNING:
            # Guardar el tiempo acumulado actual
            saved_time = current_task.elapsed_time
            print(f"Iniciando temporizador con tiempo acumulado: {saved_time} segundos")
            
            # En lugar de usar start() que reinicia el tiempo, vamos a establecer manualmente el estado
            # y calcular el tiempo de inicio para que el tiempo acumulado se mantenga
            current_task.timer.state = TimerState.RUNNING
            current_task.timer.start_time = time.time() - saved_time
        
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
                    
                    # Aplica el efecto de cambio de color con transición suave
                    # Solo cambiar el color cada 5 segundos para un efecto más suave
                    if elapsed % 5 == 0:
                        display_title.color = colors[color_index % len(colors)]
                        # Cambia también el color del borde del temporizador para un efecto visual más integrado
                        timer_container.bgcolor = ft.Colors.with_opacity(0.15, colors[color_index % len(colors)])
                        # También cambia el color del texto del temporizador para mejor integración visual
                        timer_text.color = colors[color_index % len(colors)]
                        color_index += 1
                    
                    # Actualiza la página
                    page.update()
                
                # Ajusta el tamaño del título, la nota y el temporizador según el tamaño de la ventana
                # y la orientación (portrait/landscape) - esto se hace menos frecuentemente
                if elapsed % 5 == 0:
                    sizes = calculate_font_sizes(page, font_size_multiplier)
                    display_title.size = sizes["title"]
                    display_note.size = sizes["note"]
                    timer_text.size = sizes["timer"]
                
                # Espera un tiempo más corto para actualizar más frecuentemente
                # Esto permite una actualización más fluida del temporizador
                await asyncio.sleep(0.1)  # Actualizar cada 100ms para mayor fluidez
            except Exception as e:
                print(f"Error en update_display: {e}")
                break
        
        print("Temporizador detenido")
    
    # Función para agregar una tarea a la lista
    def add_task_to_list():
        nonlocal tasks, current_task_index
        
        # Verificar que haya un título
        if not title_input.value or title_input.value.strip() == "":
            # Mostrar mensaje de error
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor ingresa un título para la tarea"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Crear una nueva tarea
        new_task = TaskFactory.create_task(title_input.value, note_input.value, link_input.value)
        tasks.append(new_task)
        
        # Guardar la tarea en la base de datos
        db.save_task(new_task)
        
        # Si es la primera tarea, establecer el índice actual
        if current_task_index == -1:
            current_task_index = 0
        
        # Limpiar los campos de entrada
        title_input.value = ""
        note_input.value = ""
        link_input.value = ""
        
        # Actualizar el contador de tareas
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Habilitar el botón de inicio si es la primera tarea
        if len(tasks) == 1:
            start_button.disabled = False
        
        # Actualizar la lista de tareas si la pantalla de configuración está visible
        if config_container.visible:
            update_task_list()
        
        # Mostrar mensaje de confirmación
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{new_task.title}' agregada correctamente"))
        page.snack_bar.open = True
        
        page.update()
    
    # Función para mostrar la pantalla de configuración
    def show_settings_screen(e=None):
        # Asegurarse de que todos los contenedores estén en la página
        if len(page.controls) == 0 or (len(page.controls) > 0 and page.controls[0] != welcome_container):
            # Restaurar todos los contenedores principales
            page.controls = [welcome_container, task_container, config_container]
        
        # Ocultar las pantallas actuales
        welcome_container.visible = False
        task_container.visible = False
        
        # Cargar las tareas eliminadas - Forzar una recarga completa desde la base de datos
        deleted_tasks = db.load_deleted_tasks()
        print(f"Mostrando pantalla de configuración con {len(deleted_tasks)} tareas eliminadas")
        
        # Función para depurar el problema con el botón de limpiar
        def debug_clear_deleted(e):
            print("Botón de limpiar historial presionado")
            clear_deleted_tasks(e)
        
        # Crear la pantalla de configuración con las tareas eliminadas
        settings_view = create_settings_screen(
            page,
            tasks,
            current_task_index,
            timer_running,
            timer_paused,
            edit_task,
            delete_task,
            close_settings_screen,
            deleted_tasks,
            restore_task,
            debug_clear_deleted,  # Usar la función de depuración
            export_tasks_to_csv   # Pasar la función de exportación a CSV
        )
        
        # Actualizar el contenido del contenedor de configuración
        config_container.content = settings_view
        
        # Mostrar la pantalla de configuración
        config_container.visible = True
        
        page.update()
    
    # Función para restaurar una tarea eliminada
    def restore_task(deleted_task_index):
        # Cargar las tareas eliminadas
        deleted_tasks = db.load_deleted_tasks()
        
        # Verificar que el índice sea válido
        if deleted_task_index < 0 or deleted_task_index >= len(deleted_tasks):
            print(f"Error: Índice de tarea eliminada inválido para restaurar: {deleted_task_index}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Error al restaurar la tarea"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Obtener la tarea eliminada
        deleted_task = deleted_tasks[deleted_task_index]
        
        # Crear una nueva tarea con los mismos datos
        new_task = TaskFactory.create_task(
            title=deleted_task.title,
            note=deleted_task.note,
            link=getattr(deleted_task, 'link', None)
        )
        
        # Establecer el tiempo acumulado
        elapsed_time = getattr(deleted_task, 'elapsed_time', 0)
        print(f"Restaurando tarea con tiempo acumulado: {elapsed_time} segundos")
        new_task.elapsed_time = elapsed_time
        
        # Asegurarse de que el temporizador tenga el tiempo correcto
        new_task.timer.set_elapsed_time(elapsed_time)
        
        # Agregar la tarea a la lista de tareas
        tasks.append(new_task)
        
        # Guardar la tarea en la base de datos
        saved_task = db.save_task(new_task)
        if saved_task:
            print(f"Tarea restaurada guardada con ID: {saved_task.id}")
        else:
            print("Error al guardar la tarea restaurada en la base de datos")
        
        # Eliminar la tarea de la tabla de tareas eliminadas
        # Esto evita que aparezca en la lista de tareas eliminadas
        if hasattr(deleted_task, 'id'):
            try:
                # Eliminar directamente de la tabla deleted_tasks
                with db.lock:
                    db.cursor.execute("DELETE FROM deleted_tasks WHERE id = ?", (deleted_task.id,))
                    db.connection.commit()
                    print(f"Tarea eliminada de la tabla deleted_tasks con ID: {deleted_task.id}")
            except Exception as e:
                print(f"Error al eliminar tarea restaurada del historial: {e}")
        
        # Actualizar el contador de tareas
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Habilitar el botón de inicio si es la primera tarea
        if len(tasks) == 1:
            start_button.disabled = False
        
        # Mostrar mensaje de confirmación
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{deleted_task.title}' restaurada con tiempo: {format_time(elapsed_time)}"))
        page.snack_bar.open = True
        
        # Actualizar la pantalla de configuración inmediatamente
        show_settings_screen()
    
    # Función para limpiar todas las tareas eliminadas
    def clear_deleted_tasks(e=None):
        print(f"clear_deleted_tasks llamada con parámetro: {e}")
        
        # Comprobar directamente si hay tareas eliminadas
        deleted_tasks = db.load_deleted_tasks()
        print(f"Hay {len(deleted_tasks)} tareas eliminadas para borrar")
        
        if len(deleted_tasks) == 0:
            # No hay tareas para eliminar
            page.snack_bar = ft.SnackBar(content=ft.Text("No hay tareas eliminadas para limpiar"))
            page.snack_bar.open = True
            page.update()
            return
        
        # ELIMINAR DIRECTAMENTE SIN DIÁLOGO
        print("Eliminando tareas sin diálogo de confirmación")
        
        # Ejecutar directamente la consulta SQL para asegurar que se eliminan
        try:
            with db.lock:
                db.cursor.execute("DELETE FROM deleted_tasks")
                db.connection.commit()
                print("Consulta SQL de eliminación ejecutada directamente")
                
                # Verificar que se hayan eliminado
                db.cursor.execute("SELECT COUNT(*) FROM deleted_tasks")
                count_after = db.cursor.fetchone()[0]
                print(f"Después de eliminar, quedan {count_after} tareas eliminadas")
        except Exception as e:
            print(f"Error al eliminar tareas: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al eliminar tareas: {e}"),
                bgcolor=ft.Colors.RED_700,
                action="OK"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Mostrar mensaje de confirmación
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Historial de tareas eliminadas limpiado"),
            bgcolor=ft.Colors.GREEN_700,
            action="OK"
        )
        page.snack_bar.open = True
        
        # Forzar la recarga de la pantalla de configuración
        # Primero limpiar el contenedor
        config_container.content = None
        page.update()
        
        # Luego recargar la pantalla de configuración
        show_settings_screen()
    
    # Función para cerrar la pantalla de configuración
    def close_settings_screen(e=None):
        # Asegurarse de que todos los contenedores estén en la página
        if len(page.controls) == 0 or page.controls[0] != welcome_container:
            # Restaurar todos los contenedores principales
            page.controls = [welcome_container, task_container, config_container]
        
        # Ocultar la pantalla de configuración
        config_container.visible = False
        
        # Mostrar la pantalla de inicio
        welcome_container.visible = True
        task_container.visible = False
        
        # Actualizar el contador de tareas
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Habilitar o deshabilitar el botón de inicio según si hay tareas
        start_button.disabled = len(tasks) == 0
        
        page.update()
    
    # Función para editar una tarea (ahora solo se usa como respaldo)
    def edit_task(task_index):
        nonlocal current_task_index
        
        # Debug print para verificar que la función se está llamando
        print(f"DEBUG: edit_task llamada con índice {task_index}")
        
        # Verificar que el índice sea válido
        if task_index < 0 or task_index >= len(tasks):
            print(f"Error: Índice de tarea inválido para editar: {task_index}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Error al editar la tarea"))
            page.snack_bar.open = True
            page.update()
            return
        
        print(f"Editando tarea {task_index + 1}: {tasks[task_index].title}")
        
        # Guardar el estado actual de las pantallas
        was_in_config = config_container.visible
        was_in_task = task_container.visible
        was_in_welcome = welcome_container.visible
        
        # Ocultar todas las pantallas actuales
        welcome_container.visible = False
        task_container.visible = False
        config_container.visible = False
        
        # Crear campos para la vista de edición
        edit_title_field = ft.TextField(
            value=tasks[task_index].title,
            label="Título",
            border_radius=10,
            expand=True,
        )
        
        edit_note_field = ft.TextField(
            value=tasks[task_index].note if tasks[task_index].note else "",
            label="Nota",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=10,
            expand=True,
        )
        
        edit_link_field = ft.TextField(
            value=tasks[task_index].link if hasattr(tasks[task_index], 'link') and tasks[task_index].link else "",
            label="Enlace",
            border_radius=10,
            expand=True,
        )
        
        # Función para cancelar la edición
        def cancel_edit(e):
            # Restaurar la pantalla anterior
            if was_in_config:
                # Restaurar la pantalla de configuración
                page.controls = [config_container]
                config_container.visible = True
            elif was_in_task:
                # Restaurar la pantalla de tareas
                page.controls = [welcome_container, task_container, config_container]
                task_container.visible = True
            else:
                # Restaurar la pantalla de inicio
                page.controls = [welcome_container, task_container, config_container]
                welcome_container.visible = True
            page.update()
        
        # Función para guardar los cambios
        def save_edit(e):
            # Verificar que el título no esté vacío
            if not edit_title_field.value or edit_title_field.value.strip() == "":
                page.snack_bar = ft.SnackBar(content=ft.Text("El título de la tarea no puede estar vacío"))
                page.snack_bar.open = True
                page.update()
                return
                
            # Guardar los cambios
            save_task_changes(task_index, edit_title_field, edit_note_field, edit_link_field)
            
            # Restaurar la pantalla anterior
            if was_in_config:
                # Restaurar la pantalla de configuración
                page.controls = [config_container]
                config_container.visible = True
                # Actualizar la pantalla de configuración
                show_settings_screen()
            elif was_in_task:
                # Restaurar la pantalla de tareas
                page.controls = [welcome_container, task_container, config_container]
                task_container.visible = True
            else:
                # Restaurar la pantalla de inicio
                page.controls = [welcome_container, task_container, config_container]
                welcome_container.visible = True
            
            page.update()
        
        # Crear la pantalla de edición
        edit_screen = ft.Column([
            # Encabezado
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.BLUE_700,
                        tooltip="Volver",
                        on_click=cancel_edit
                    ),
                    ft.Text(
                        f"Editar Tarea {task_index + 1}",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                ]),
                margin=ft.margin.only(bottom=20),
            ),
            # Campos de edición
            ft.Container(
                content=ft.Column([
                    edit_title_field,
                    ft.Container(height=10),
                    edit_note_field,
                    ft.Container(height=10),
                    edit_link_field,
                ]),
                padding=20,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                margin=ft.margin.only(bottom=20),
            ),
            # Botones
            ft.Row([
                ft.ElevatedButton(
                    text="Cancelar",
                    icon=ft.Icons.CANCEL,
                    on_click=cancel_edit,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700,
                    ),
                ),
                ft.ElevatedButton(
                    text="Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=save_edit,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_700,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
        ], spacing=10, expand=True)
        
        # Crear un contenedor para la pantalla de edición
        edit_screen_container = ft.Container(
            content=edit_screen,
            expand=True,
            padding=20,
            bgcolor=ft.Colors.WHITE,
        )
        
        # Reemplazar el contenido de la página con la pantalla de edición
        # Esto asegura que aparezca en la parte superior
        page.controls = [edit_screen_container]
        page.scroll = "auto"  # Permitir desplazamiento si es necesario
        page.update()
        page.update()
    
    # Función para eliminar una tarea
    def delete_task(task_index):
        nonlocal tasks, current_task_index, timer_running, timer_paused
        
        # Verificar que el índice sea válido
        if task_index < 0 or task_index >= len(tasks):
            print(f"Error: Índice de tarea inválido para eliminar: {task_index}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Error al eliminar la tarea"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Obtener la tarea a eliminar
        task_to_delete = tasks[task_index]
        task_id = getattr(task_to_delete, 'id', None)
        task_name = task_to_delete.title
        
        print(f"Intentando eliminar tarea con ID: {task_id}")
        
        # Si la tarea que se está eliminando es la actual, detener el temporizador
        if task_index == current_task_index:
            task_to_delete.timer.stop()
            timer_running = False
            timer_paused = False
        
        # Guardar el tiempo acumulado para asegurarnos de que se preserve
        # Asegurarnos de obtener el tiempo acumulado más reciente
        if task_to_delete.timer.state == TimerState.RUNNING:
            # Si el temporizador está corriendo, obtener el tiempo actualizado
            elapsed_time = task_to_delete.timer.get_elapsed_time()
            print(f"Temporizador en ejecución, tiempo actualizado: {elapsed_time} segundos")
        else:
            # Si el temporizador está detenido o pausado, usar el tiempo guardado
            elapsed_time = task_to_delete.elapsed_time
            print(f"Temporizador no en ejecución, tiempo guardado: {elapsed_time} segundos")
        
        # Actualizar el tiempo acumulado en la tarea antes de eliminarla
        task_to_delete.elapsed_time = elapsed_time
        task_to_delete.timer.set_elapsed_time(elapsed_time)
        print(f"Tiempo acumulado final de la tarea a eliminar: {elapsed_time} segundos")
        
        # Guardar la tarea en la tabla de tareas eliminadas antes de eliminarla
        if task_id:
            # Asegurarse de que la tarea tenga todos los atributos necesarios
            if not hasattr(task_to_delete, 'link'):
                task_to_delete.link = ""
            
            # Intentar eliminar la tarea de la base de datos (esto la mueve a deleted_tasks)
            # Pasar el tiempo acumulado actualizado para asegurar que se preserve
            success = db.delete_task(task_id, elapsed_time)
            if success:
                print(f"Tarea guardada en deleted_tasks con ID: {task_id} y tiempo: {elapsed_time} segundos")
            else:
                print(f"Error al guardar la tarea en deleted_tasks")
                # Intentar insertar directamente en la tabla deleted_tasks como respaldo
                try:
                    with db.lock:
                        db.cursor.execute('''
                        INSERT INTO deleted_tasks (title, note, link, elapsed_time)
                        VALUES (?, ?, ?, ?)
                        ''', (
                            task_to_delete.title,
                            task_to_delete.note,
                            getattr(task_to_delete, 'link', ''),
                            elapsed_time
                        ))
                        db.connection.commit()
                        print(f"Tarea insertada directamente en deleted_tasks como respaldo")
                except Exception as e:
                    print(f"Error al insertar directamente en deleted_tasks: {e}")
        else:
            # Si la tarea no tiene ID, primero guardarla en la base de datos para obtener un ID
            print(f"La tarea no tiene ID, intentando guardarla primero")
            try:
                # Guardar la tarea para obtener un ID
                saved_task = db.save_task(task_to_delete)
                if saved_task:
                    task_id = saved_task.id
                    print(f"Tarea guardada con nuevo ID: {task_id}")
                    
                    # Ahora intentar moverla a deleted_tasks
                    # Pasar el tiempo acumulado actualizado para asegurar que se preserve
                    success = db.delete_task(task_id, elapsed_time)
                    if success:
                        print(f"Tarea guardada en deleted_tasks con ID: {task_id} y tiempo: {elapsed_time} segundos")
                    else:
                        print(f"Error al guardar la tarea en deleted_tasks")
                        # Intentar insertar directamente como respaldo
                        try:
                            with db.lock:
                                db.cursor.execute('''
                                INSERT INTO deleted_tasks (title, note, link, elapsed_time)
                                VALUES (?, ?, ?, ?)
                                ''', (
                                    task_to_delete.title,
                                    task_to_delete.note,
                                    getattr(task_to_delete, 'link', ''),
                                    elapsed_time
                                ))
                                db.connection.commit()
                                print(f"Tarea insertada directamente en deleted_tasks como respaldo")
                        except Exception as e:
                            print(f"Error al insertar directamente en deleted_tasks: {e}")
                else:
                    print(f"No se pudo obtener un ID para la tarea")
                    # Intentar insertar directamente como respaldo
                    try:
                        with db.lock:
                            db.cursor.execute('''
                            INSERT INTO deleted_tasks (title, note, link, elapsed_time)
                            VALUES (?, ?, ?, ?)
                            ''', (
                                task_to_delete.title,
                                task_to_delete.note,
                                getattr(task_to_delete, 'link', ''),
                                elapsed_time
                            ))
                            db.connection.commit()
                            print(f"Tarea insertada directamente en deleted_tasks como respaldo")
                    except Exception as e:
                        print(f"Error al insertar directamente en deleted_tasks: {e}")
            except Exception as e:
                print(f"Error al intentar guardar la tarea: {e}")
        
        # Eliminar la tarea de la lista en memoria
        print(f"Eliminando tarea {task_index + 1}: {task_name}")
        tasks.pop(task_index)
        
        print(f"Tarea eliminada. Quedan {len(tasks)} tareas.")
        
        # Actualizar el contador de tareas
        task_list_text.value = f"Tareas agregadas: {len(tasks)}"
        
        # Si no hay tareas, deshabilitar el botón de inicio
        if len(tasks) == 0:
            start_button.disabled = True
        else:
            # Ajustar el índice de la tarea actual si es necesario
            if current_task_index >= len(tasks):
                current_task_index = len(tasks) - 1
            elif current_task_index > task_index:
                current_task_index -= 1
            
            # Actualizar la interfaz con la tarea actual si estamos en la pantalla de tareas
            if not config_container.visible and current_task_index >= 0:
                display_title.value = tasks[current_task_index].title
                display_note.value = tasks[current_task_index].note
                
                # Actualizar el indicador de posición y los botones de navegación
                task_position_text.value = f"Tarea {current_task_index + 1} de {len(tasks)}"
                prev_task_button.visible = current_task_index > 0
                next_task_button.visible = current_task_index < len(tasks) - 1
        
        # Mostrar mensaje de confirmación
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{task_name}' eliminada correctamente"))
        page.snack_bar.open = True
        
        # Actualizar la lista de tareas
        update_task_list()
        
        # Verificar si estamos en la pantalla de configuración y actualizarla
        # para mostrar la tarea en la lista de eliminados inmediatamente
        if config_container.visible:
            # Actualizar la pantalla de configuración en tiempo real
            show_settings_screen()
        
        page.update()
    
    # Función para confirmar la eliminación de una tarea
    def confirm_delete_task(task_index, dialog):
        # Cerrar el diálogo de confirmación
        dialog.open = False
        page.update()
    
    # Función para actualizar la lista de tareas en la pantalla de configuración
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
        
        # Habilitar o deshabilitar el botón de inicio según si hay tareas
        start_button.disabled = len(tasks) == 0
        
        page.update()
    
    # Función para crear un elemento de tarea con edición in-line
    def create_task_item(index, task, time_str):
        # Crear un contenedor para la vista normal (no edición)
        normal_view = ft.Column([
            ft.Row([
                ft.Text(f"Tarea {index+1}", weight=ft.FontWeight.BOLD),
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
        
        # Crear campos para la vista de edición
        edit_title_field = ft.TextField(
            value=task.title,
            label="Título",
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
        
        edit_link_field = ft.TextField(
            value=task.link if hasattr(task, 'link') and task.link else "",
            label="Enlace",
            border_radius=10,
            width=400,
        )
        
        # Crear un contenedor para la vista de edición
        edit_view = ft.Column([
            ft.Row([
                ft.Text(f"Editando Tarea {index+1}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Tiempo: {time_str}", color=ft.Colors.BLUE_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            edit_title_field,
            edit_note_field,
            edit_link_field,
            ft.Row([
                ft.ElevatedButton(
                    text="Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e, idx=index, tf=edit_title_field, nf=edit_note_field, lf=edit_link_field: save_task_changes(idx, tf, nf, lf),
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
            data={"normal_view": normal_view, "edit_view": edit_view, "index": index}  # Guardar referencias para acceso fácil
        )
        
        return task_container
    
    # Función para alternar entre modo de visualización y edición
    def toggle_edit_mode(task_index, cancel=False):
        # Buscar el contenedor de la tarea por su índice
        for task_container in task_list.controls:
            if hasattr(task_container, "data") and task_container.data.get("index") == task_index:
                normal_view = task_container.data["normal_view"]
                edit_view = task_container.data["edit_view"]
                
                # Alternar la visibilidad de las vistas
                normal_view.visible = not normal_view.visible
                edit_view.visible = not edit_view.visible
                
                # Si estamos cancelando, no hacemos nada más
                if not cancel and edit_view.visible:
                    # Estamos entrando en modo de edición
                    print(f"Editando tarea {task_index + 1}: {tasks[task_index].title}")
                
                page.update()
                break
    
    # Función para guardar los cambios en una tarea
    def save_task_changes(task_index, title_field, note_field, link_field=None):
        # Verificar que el título no esté vacío
        if not title_field.value or title_field.value.strip() == "":
            page.snack_bar = ft.SnackBar(content=ft.Text("El título de la tarea no puede estar vacío"))
            page.snack_bar.open = True
            page.update()
            return False
        
        # Guardar el título anterior para el mensaje de confirmación
        old_title = tasks[task_index].title
        
        print(f"Guardando cambios en tarea {task_index + 1}")
        print(f"  Título anterior: {old_title}")
        print(f"  Título nuevo: {title_field.value}")
        print(f"  Nota nueva: {note_field.value}")
        if link_field:
            print(f"  Enlace nuevo: {link_field.value}")
        
        # Actualizar la tarea
        tasks[task_index].title = title_field.value
        tasks[task_index].note = note_field.value
        
        # Actualizar el enlace si se proporcionó
        if link_field:
            tasks[task_index].link = link_field.value
            
        # Guardar los cambios en la base de datos
        db.save_all_tasks(tasks)  # Guardar todas las tareas para asegurar persistencia
        
        # Si la tarea actual es la que se está editando, actualizar la interfaz principal
        if task_index == current_task_index:
            display_title.value = title_field.value
            display_note.value = note_field.value
            
            # Actualizar el enlace en la interfaz principal
            if link_field:
                link_value = link_field.value
                display_link.text = link_value if link_value else "Sin enlace"
                display_link.url = link_value if link_value else None
                display_link.tooltip = "Haz clic para abrir el enlace" if link_value else "No hay enlace disponible"
                display_link.style.color = ft.Colors.BLUE_700 if link_value else ft.Colors.GREY_400
                display_link.disabled = not link_value
        
        # Actualizar la lista de tareas para reflejar los cambios
        update_task_list()
        
        # Mostrar mensaje de confirmación
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Tarea '{title_field.value}' actualizada correctamente"))
        page.snack_bar.open = True
        
        page.update()
        return True
    
    # Función para exportar tareas a CSV
    def export_tasks_to_csv(e=None):
        # Función para exportar todas las tareas (activas y eliminadas) a un archivo CSV
        try:
            # Cargar las tareas eliminadas desde la base de datos
            deleted_tasks = db.load_deleted_tasks()
            
            # Verificar si hay tareas para exportar (activas o eliminadas)
            if len(tasks) == 0 and len(deleted_tasks) == 0:
                page.snack_bar = ft.SnackBar(content=ft.Text("No hay tareas para exportar"))
                page.snack_bar.open = True
                page.update()
                return
            
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
                csv_writer.writerow(["Tarea", "Titulo", "Nota", "Enlace", "Tiempo (segundos)", "Tiempo (formato)", "Estado", "Fecha Eliminacion"])
                
                # Escribir datos de cada tarea activa
                for i, task in enumerate(tasks):
                    # Manejar comillas dobles en título, nota y enlace
                    title = task.title.replace('"', "'")
                    note = task.note.replace('"', "'") if task.note else ""
                    link = task.link.replace('"', "'") if hasattr(task, 'link') and task.link else ""
                    
                    # Obtener el tiempo formateado
                    time_str = format_time(task.elapsed_time)
                    
                    # Escribir fila (tareas activas)
                    csv_writer.writerow([i+1, title, note, link, task.elapsed_time, time_str, "Activa", ""])
                
                # Escribir datos de cada tarea eliminada
                for i, task in enumerate(deleted_tasks):
                    # Manejar comillas dobles en título, nota y enlace
                    title = task.title.replace('"', "'")
                    note = task.note.replace('"', "'") if task.note else ""
                    link = task.link.replace('"', "'") if hasattr(task, 'link') and task.link else ""
                    
                    # Obtener el tiempo formateado
                    time_str = format_time(task.elapsed_time)
                    
                    # Obtener la fecha de eliminación y convertirla de UTC a hora local
                    deleted_date = ""
                    if hasattr(task, 'deleted_at') and task.deleted_at:
                        try:
                            # Parsear la fecha de SQLite (formato ISO)
                            utc_date = datetime.datetime.fromisoformat(task.deleted_at.replace(' ', 'T'))
                            # Convertir a hora local
                            local_date = utc_date.replace(tzinfo=datetime.timezone.utc).astimezone()
                            # Formatear la fecha en un formato legible
                            deleted_date = local_date.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception as e:
                            print(f"Error al convertir fecha: {e}")
                            deleted_date = task.deleted_at  # Usar la fecha original si hay error
                    
                    # Escribir fila (tareas eliminadas)
                    csv_writer.writerow([len(tasks) + i + 1, title, note, link, task.elapsed_time, time_str, "Eliminada", deleted_date])
            
            # Mostrar mensaje de éxito en snackbar con la ruta del archivo
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Archivo CSV exportado exitosamente a: {filepath}"),
                bgcolor=ft.Colors.GREEN_700,
                action="OK"
            )
            page.snack_bar.open = True
            
            # Asegurarse de que el contenedor de información sea visible y esté en primer plano
            download_info_container.visible = True
            download_path_text.value = f"Archivo CSV guardado en: {filepath}"
            download_path_text.visible = True
            
            # Forzar la actualización de la página para mostrar el mensaje
            page.update()
            
            print(f"Archivo CSV exportado exitosamente a: {filepath}")
            print(f"Total de tareas exportadas: {len(tasks)} activas, {len(deleted_tasks)} eliminadas")
            
        except Exception as e:
            # Mostrar mensaje de error
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al exportar tareas: {str(e)}"))
            page.snack_bar.open = True
            page.update()
            print(f"Error al exportar tareas a CSV: {str(e)}")
    
    # Función para regresar a la pantalla de inicio
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
        
        # Actualizar la página
        page.update()
    
    # Función para navegar entre tareas
    def navigate_task(direction):
        nonlocal current_task_index, timer_running, timer_paused
        
        # Obtener la tarea actual
        current_task = tasks[current_task_index]
        
        # Pausar el temporizador de la tarea actual si está corriendo
        if current_task.timer.state == TimerState.RUNNING:
            current_task.timer.pause()
            timer_running = False
            timer_paused = True
        
        # Calcular el nuevo índice
        new_index = current_task_index + direction
        
        # Verificar que el índice esté dentro de los límites
        if 0 <= new_index < len(tasks):
            current_task_index = new_index
            
            # Obtener la nueva tarea actual
            new_current_task = tasks[current_task_index]
            
            # Cargar la tarea actual
            display_title.value = new_current_task.title
            display_note.value = new_current_task.note
            
            # Actualizar el enlace
            link_value = new_current_task.link if hasattr(new_current_task, 'link') else ""
            display_link.text = link_value if link_value else "Sin enlace"
            display_link.url = link_value if link_value else None
            display_link.tooltip = "Haz clic para abrir el enlace" if link_value else "No hay enlace disponible"
            display_link.style.color = ft.Colors.BLUE_700 if link_value else ft.Colors.GREY_400
            display_link.disabled = not link_value
            
            # Establecer el tiempo guardado para esta tarea
            elapsed_time = new_current_task.elapsed_time
            
            # Actualizar el texto del temporizador
            timer_text.value = format_time(elapsed_time)
            
            # Actualizar el indicador de posición
            task_position_text.value = f"Tarea {current_task_index + 1} de {len(tasks)}"
            
            # Actualizar visibilidad de los botones de navegación
            prev_task_button.visible = current_task_index > 0
            next_task_button.visible = current_task_index < len(tasks) - 1
            
            # Actualizar el botón de pausa/reanudación según el estado de la nueva tarea
            if new_current_task.timer.state == TimerState.RUNNING:
                pause_resume_button.icon = ft.Icons.PAUSE
                timer_running = True
                timer_paused = False
            else:  # PAUSED o STOPPED
                pause_resume_button.icon = ft.Icons.PLAY_ARROW
                timer_running = False
                timer_paused = (new_current_task.timer.state == TimerState.PAUSED)
        
        # Actualizar la página
        page.update()
    
    # Función para iniciar el temporizador desde la pantalla de inicio
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
        
        # Actualizar el enlace
        link_value = current_task.link if hasattr(current_task, 'link') else ""
        display_link.text = link_value if link_value else "Sin enlace"
        display_link.url = link_value if link_value else None
        display_link.tooltip = "Haz clic para abrir el enlace" if link_value else "No hay enlace disponible"
        display_link.style.color = ft.Colors.BLUE_700 if link_value else ft.Colors.GREY_400
        display_link.disabled = not link_value
        
        # Establecer el tiempo guardado para esta tarea
        elapsed_time = current_task.elapsed_time
        timer_text.value = format_time(elapsed_time)
        
        # Actualizar el indicador de posición
        task_position_text.value = f"Tarea {current_task_index + 1} de {len(tasks)}"
        
        # Actualizar visibilidad de los botones de navegación
        prev_task_button.visible = current_task_index > 0
        next_task_button.visible = current_task_index < len(tasks) - 1
        
        # Configurar el botón de pausa/reanudación para iniciar (no iniciar automáticamente)
        timer_running = False
        timer_paused = False
        pause_resume_button.icon = ft.Icons.PLAY_ARROW
        
        # Mostrar la pantalla de tareas y ocultar la pantalla de inicio
        welcome_container.visible = False
        task_container.visible = True
        
        # Actualizar la página
        page.update()
        
        # No iniciamos la actualización del temporizador automáticamente
        # Solo se iniciará cuando el usuario haga clic en el botón de reproducción
    
    # Crear botones para la pantalla de inicio
    start_button = create_button(
        text="INICIAR",
        icon=ft.Icons.PLAY_ARROW,
        on_click=start_button_clicked,
        color=ft.Colors.GREEN_700
    )
    
    # Deshabilitar el botón de inicio si no hay tareas
    start_button.disabled = True
    
    add_task_button = create_button(
        text="AGREGAR TAREA",
        icon=ft.Icons.ADD_TASK,
        on_click=lambda e: add_task_to_list(),
        color=ft.Colors.GREEN_700
    )
    
    settings_button = create_button(
        text="CONFIGURACIÓN",
        icon=ft.Icons.SETTINGS,
        on_click=show_settings_screen,
        color=ft.Colors.BLUE_700
    )
    
    # Configurar eventos para los botones de navegación y control
    prev_task_button.on_click = lambda e: navigate_task(-1)
    next_task_button.on_click = lambda e: navigate_task(1)
    pause_resume_button.on_click = pause_resume_timer
    home_button.on_click = lambda e: return_to_home()
    
    # Crear la pantalla de bienvenida
    welcome_container = create_welcome_screen(
        title_input, note_input, link_input, add_task_button, 
        start_button, settings_button, task_list_text
    )
    
    # Crear la pantalla de configuración
    # Encabezado
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.BLUE_700,
                    tooltip="Volver",
                    on_click=close_settings_screen
                ),
                ft.Text(
                    "Configuración de Tareas",
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
    
    # Crear un texto para mostrar la ruta de descarga (inicialmente vacío)
    download_path_text = ft.Text(
        value="",
        size=16,
        color=ft.Colors.BLACK,  # Cambiado a negro para mejor visibilidad
        selectable=True,  # Permite seleccionar el texto para copiarlo
    )
    
    # Crear un contenedor para el texto de descarga con un botón para cerrarlo
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
        border=ft.border.all(2, ft.Colors.GREEN_500),  # Borde más visible
        border_radius=10,
        bgcolor="#E8F5E9",  # Color de fondo verde claro
        margin=ft.margin.only(bottom=15, top=10),  # Más espacio
        visible=False,  # Inicialmente oculto
    )
    
    # Función para mostrar u ocultar la información de descarga
    def set_download_info_visible(visible, path=""):
        download_info_container.visible = visible
        if visible and path:
            download_path_text.value = f"Archivo CSV guardado en: {path}"
            # Asegurarse de que el texto sea visible
            download_path_text.visible = True
        page.update()
    
    # Crear una columna para la pantalla de configuración
    settings_screen = ft.Column(
        [
            header,
            download_info_container,  # Agregar el contenedor de información de descarga
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
    
    # Contenedor principal para la pantalla de configuración
    config_container = ft.Container(
        content=settings_screen,
        expand=True,
        padding=20,
        bgcolor=ft.Colors.WHITE,
        visible=False
    )
    
    # Actualizar la lista de tareas antes de mostrar la pantalla de bienvenida
    update_task_list()
    
    # Inicialmente, mostrar la pantalla de bienvenida y ocultar las demás
    welcome_container.visible = True
    task_container.visible = False
    config_container.visible = False
    
    # Añadir los contenedores a la página
    page.add(
        ft.Container(
            content=ft.Stack([welcome_container, task_container, config_container]),
            expand=True,
            padding=0
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
