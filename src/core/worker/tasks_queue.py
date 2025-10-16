from typing import Callable

from src.core.interfaces.tasks_queue import AbstractTaskQueue
from src.core.worker.celery import get_route_tasks
from src.core.worker.exceptions import TaskDoesntExist

class CeleryTaskQueue(AbstractTaskQueue):

    def __init__(self, app):
        self.app = app

    def execute(
            self, 
            func: Callable, 
            *func_args, 
            **task_kwargs):
        func_name = func.__name__
        route_tasks = get_route_tasks()
        for route in route_tasks:
            if route == func_name:
                task = route_tasks[route]
                realization_name = func.__qualname__
                return task.apply_async((realization_name, *func_args), **task_kwargs)
        raise TaskDoesntExist