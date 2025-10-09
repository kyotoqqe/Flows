from typing import Callable

from src.core.worker.celery import app

@app.task
def execute(func: Callable, *args, **kwargs):
    return func(*args, **kwargs)

def add(x: int, y: int):
    return x + y

def divide(x: int, y: int):
    return x / y

