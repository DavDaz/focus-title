import sqlite3
import os
import threading
from models import Task, TaskFactory, TimerState

class Database:
    def __init__(self, db_path="focus_title.db"):
        """
        Inicializa la conexión a la base de datos.
        Si no existe, la crea con la estructura necesaria.
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.lock = threading.Lock()  # Para sincronizar acceso a la base de datos
        self.thread_local = threading.local()  # Almacenamiento local por hilo
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establece la conexión a la base de datos"""
        try:
            # Usar check_same_thread=False para permitir acceso desde diferentes hilos
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
            self.cursor = self.connection.cursor()
            print(f"Conexión establecida a la base de datos: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
    
    def create_tables(self):
        """Crea las tablas necesarias si no existen"""
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                note TEXT,
                link TEXT,
                elapsed_time INTEGER DEFAULT 0,
                timer_state INTEGER DEFAULT 0
            )
            ''')
            
            # Crear tabla para tareas eliminadas
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deleted_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                note TEXT,
                link TEXT,
                elapsed_time INTEGER DEFAULT 0,
                deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            self.connection.commit()
            print("Tablas creadas o verificadas correctamente")
        except sqlite3.Error as e:
            print(f"Error al crear las tablas: {e}")
    
    def save_task(self, task):
        """
        Guarda una tarea en la base de datos.
        Si la tarea ya existe (tiene id), la actualiza.
        """
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            try:
                # Verificar si la tarea ya tiene un ID (para actualización)
                task_id = getattr(task, 'id', None)
                
                # Asegurarnos de obtener el tiempo acumulado más reciente
                elapsed_time = task.elapsed_time
                if task.timer.state == TimerState.RUNNING:
                    # Si el temporizador está corriendo, obtener el tiempo actualizado
                    elapsed_time = task.timer.get_elapsed_time()
                    print(f"Guardando tarea con temporizador en ejecución, tiempo actualizado: {elapsed_time} segundos")
                else:
                    print(f"Guardando tarea con temporizador no en ejecución, tiempo: {elapsed_time} segundos")
                
                if task_id:
                    # Actualizar tarea existente
                    self.cursor.execute('''
                    UPDATE tasks 
                    SET title = ?, note = ?, link = ?, elapsed_time = ?, timer_state = ?
                    WHERE id = ?
                    ''', (
                        task.title, 
                        task.note, 
                        getattr(task, 'link', ''),
                        elapsed_time,  # Usar el tiempo actualizado
                        task.timer.state.value,
                        task_id
                    ))
                else:
                    # Insertar nueva tarea
                    self.cursor.execute('''
                    INSERT INTO tasks (title, note, link, elapsed_time, timer_state)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        task.title, 
                        task.note, 
                        getattr(task, 'link', ''),
                        elapsed_time,  # Usar el tiempo actualizado
                        task.timer.state.value
                    ))
                    # Obtener el ID generado y asignarlo a la tarea
                    task.id = self.cursor.lastrowid
                
                self.connection.commit()
                return task
            except sqlite3.Error as e:
                print(f"Error al guardar la tarea: {e}")
                return None
    
    def save_all_tasks(self, tasks):
        """Guarda todas las tareas en la base de datos"""
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            try:
                # Primero eliminar todas las tareas existentes
                self.cursor.execute("DELETE FROM tasks")
                
                # Luego insertar todas las tareas actuales
                for task in tasks:
                    # Insertar directamente sin llamar a save_task para evitar bloqueos anidados
                    task_id = getattr(task, 'id', None)
                    
                    # Asegurarse de que el tiempo acumulado esté actualizado
                    # Si la tarea está en ejecución, calcular el tiempo acumulado actual
                    # antes de guardarlo en la base de datos
                    current_elapsed_time = task.elapsed_time
                    
                    self.cursor.execute('''
                    INSERT INTO tasks (title, note, link, elapsed_time, timer_state)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        task.title, 
                        task.note, 
                        getattr(task, 'link', ''),
                        current_elapsed_time,
                        task.timer.state.value
                    ))
                    
                    # Actualizar el ID si es una tarea nueva
                    if not task_id:
                        task.id = self.cursor.lastrowid
                
                self.connection.commit()
                print(f"Se guardaron {len(tasks)} tareas en la base de datos")
                return True
            except sqlite3.Error as e:
                print(f"Error al guardar todas las tareas: {e}")
                return False
    
    def load_tasks(self):
        """Carga todas las tareas desde la base de datos"""
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            try:
                self.cursor.execute("SELECT * FROM tasks ORDER BY id")
                rows = self.cursor.fetchall()
                
                tasks = []
                for row in rows:
                    # Crear una tarea con los datos de la base de datos
                    task = TaskFactory.create_task(
                        title=row['title'],
                        note=row['note'],
                        link=row['link']
                    )
                    
                    # Asignar el ID de la base de datos
                    task.id = row['id']
                    
                    # Establecer el tiempo acumulado
                    elapsed_time = row['elapsed_time']
                    task.elapsed_time = elapsed_time
                    
                    # Establecer el estado del temporizador
                    timer_state = row['timer_state']
                    task.timer.state = TimerState(timer_state)
                    
                    # Si el temporizador estaba en ejecución, asegurarse de que el tiempo de inicio
                    # se establezca correctamente para que el tiempo acumulado se mantenga
                    # Nota: En realidad, al cargar siempre ponemos el temporizador en estado STOPPED
                    # para evitar que siga corriendo sin control
                    task.timer.state = TimerState.STOPPED
                    
                    # Imprimir información de depuración
                    print(f"Tarea cargada: {task.title}, Tiempo: {elapsed_time} segundos")
                    
                    tasks.append(task)
                
                print(f"Se cargaron {len(tasks)} tareas desde la base de datos")
                return tasks
            except sqlite3.Error as e:
                print(f"Error al cargar las tareas: {e}")
                return []
    
    def delete_task(self, task_id, elapsed_time=None):
        """Elimina una tarea por su ID y la guarda en la tabla de tareas eliminadas
        
        Args:
            task_id: ID de la tarea a eliminar
            elapsed_time: Tiempo acumulado actualizado (opcional)
        """
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            try:
                print(f"Intentando eliminar tarea con ID: {task_id}")
                
                # Primero obtener la tarea que se va a eliminar
                self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task_row = self.cursor.fetchone()
                
                if task_row:
                    print(f"Tarea encontrada: {task_row['title']}")
                    
                    try:
                        # Determinar qué tiempo usar
                        time_to_use = elapsed_time if elapsed_time is not None else task_row['elapsed_time']
                        print(f"Tiempo acumulado en la base de datos: {task_row['elapsed_time']} segundos")
                        print(f"Tiempo acumulado proporcionado: {elapsed_time if elapsed_time is not None else 'None'} segundos")
                        print(f"Tiempo acumulado que se usará: {time_to_use} segundos")
                        
                        # Guardar la tarea en la tabla de tareas eliminadas
                        self.cursor.execute('''
                        INSERT INTO deleted_tasks (title, note, link, elapsed_time)
                        VALUES (?, ?, ?, ?)
                        ''', (
                            task_row['title'],
                            task_row['note'],
                            task_row['link'],
                            time_to_use  # Usar el tiempo proporcionado si está disponible
                        ))
                        
                        # Verificar que se haya insertado correctamente
                        deleted_id = self.cursor.lastrowid
                        print(f"Tarea guardada en deleted_tasks con ID: {deleted_id}")
                        
                        # Eliminar la tarea de la tabla principal
                        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                        self.connection.commit()
                        print(f"Tarea eliminada de la tabla principal y movida a deleted_tasks")
                        return True
                    except sqlite3.Error as inner_e:
                        print(f"Error al mover la tarea a deleted_tasks: {inner_e}")
                        # Intentar hacer rollback
                        self.connection.rollback()
                        return False
                else:
                    print(f"No se encontró ninguna tarea con ID: {task_id}")
                    return False
            except sqlite3.Error as e:
                print(f"Error al eliminar la tarea: {e}")
                # Intentar hacer rollback
                try:
                    self.connection.rollback()
                except:
                    pass
                return False
    
    def load_deleted_tasks(self):
        """Carga todas las tareas eliminadas desde la base de datos"""
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            try:
                self.cursor.execute("SELECT * FROM deleted_tasks ORDER BY deleted_at DESC")
                rows = self.cursor.fetchall()
                
                deleted_tasks = []
                for row in rows:
                    # Crear una tarea con los datos de la base de datos
                    task = TaskFactory.create_task(
                        title=row['title'],
                        note=row['note'],
                        link=row['link']
                    )
                    
                    # Asignar el ID de la base de datos
                    task.id = row['id']
                    
                    # Obtener el tiempo acumulado de la base de datos
                    elapsed_time = row['elapsed_time']
                    
                    # Establecer el tiempo acumulado en la propiedad
                    task.elapsed_time = elapsed_time
                    
                    # Asegurarse de que el temporizador tenga el tiempo correcto
                    task.timer.set_elapsed_time(elapsed_time)
                    
                    # Guardar la fecha de eliminación
                    task.deleted_at = row['deleted_at']
                    
                    print(f"Tarea eliminada cargada: {task.title}, tiempo: {elapsed_time} segundos")
                    deleted_tasks.append(task)
                
                print(f"Se cargaron {len(deleted_tasks)} tareas eliminadas desde la base de datos")
                return deleted_tasks
            except sqlite3.Error as e:
                print(f"Error al cargar las tareas eliminadas: {e}")
                return []
    
    def clear_deleted_tasks(self):
        """Elimina todas las tareas de la tabla de tareas eliminadas"""
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            try:
                # Contar cuántas tareas hay antes de eliminar
                self.cursor.execute("SELECT COUNT(*) FROM deleted_tasks")
                count_before = self.cursor.fetchone()[0]
                print(f"Intentando eliminar {count_before} tareas eliminadas")
                
                # Ejecutar la eliminación
                self.cursor.execute("DELETE FROM deleted_tasks")
                self.connection.commit()
                
                # Verificar que se hayan eliminado
                self.cursor.execute("SELECT COUNT(*) FROM deleted_tasks")
                count_after = self.cursor.fetchone()[0]
                print(f"Después de eliminar, quedan {count_after} tareas eliminadas")
                
                return True
            except sqlite3.Error as e:
                print(f"Error al limpiar las tareas eliminadas: {e}")
                return False
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            if self.connection:
                try:
                    self.connection.close()
                    print("Conexión a la base de datos cerrada")
                except Exception as e:
                    print(f"Error al cerrar la conexión a la base de datos: {e}")
