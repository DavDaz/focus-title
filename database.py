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
                        task.elapsed_time,
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
                        task.elapsed_time,
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
                    
                    self.cursor.execute('''
                    INSERT INTO tasks (title, note, link, elapsed_time, timer_state)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        task.title, 
                        task.note, 
                        getattr(task, 'link', ''),
                        task.elapsed_time,
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
                    task.elapsed_time = row['elapsed_time']
                    
                    # Establecer el estado del temporizador
                    timer_state = row['timer_state']
                    task.timer.state = TimerState(timer_state)
                    
                    tasks.append(task)
                
                print(f"Se cargaron {len(tasks)} tareas desde la base de datos")
                return tasks
            except sqlite3.Error as e:
                print(f"Error al cargar las tareas: {e}")
                return []
    
    def delete_task(self, task_id):
        """Elimina una tarea por su ID"""
        with self.lock:  # Adquirir el bloqueo para operaciones de base de datos
            try:
                self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                self.connection.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error al eliminar la tarea: {e}")
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
