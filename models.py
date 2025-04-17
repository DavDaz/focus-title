import time
from enum import Enum

# Definir estados posibles para el temporizador
class TimerState(Enum):
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2

# Clase para el temporizador de cada tarea
class TaskTimer:
    def __init__(self):
        self.state = TimerState.STOPPED
        self.elapsed_time = 0
        self.start_time = None
        self.pause_time = None
    
    def start(self):
        if self.state == TimerState.STOPPED:
            self.start_time = time.time()
            self.elapsed_time = 0
        elif self.state == TimerState.PAUSED:
            # Reanudar desde donde se quedó
            self.start_time = time.time() - self.elapsed_time
        
        self.state = TimerState.RUNNING
        return self
    
    def pause(self):
        if self.state == TimerState.RUNNING:
            self.pause_time = time.time()
            self.elapsed_time = int(self.pause_time - self.start_time)
            self.state = TimerState.PAUSED
        return self
    
    def resume(self):
        if self.state == TimerState.PAUSED:
            self.start_time = time.time() - self.elapsed_time
            self.state = TimerState.RUNNING
        return self
    
    def stop(self):
        self.state = TimerState.STOPPED
        return self
    
    def get_elapsed_time(self):
        if self.state == TimerState.RUNNING:
            current_time = time.time()
            return int(current_time - self.start_time)
        return self.elapsed_time
    
    def set_elapsed_time(self, time_value):
        self.elapsed_time = time_value
        if self.state == TimerState.RUNNING:
            self.start_time = time.time() - time_value
        return self

# Clase para las tareas
class Task:
    def __init__(self, title, note, link=None):
        self.title = title
        self.note = note
        self.link = link
        self.timer = TaskTimer()
    
    @property
    def elapsed_time(self):
        return self.timer.get_elapsed_time()
    
    @elapsed_time.setter
    def elapsed_time(self, value):
        self.timer.set_elapsed_time(value)

# Fábrica de tareas (patrón Factory)
class TaskFactory:
    @staticmethod
    def create_task(title, note, link=None):
        return Task(title, note, link)
