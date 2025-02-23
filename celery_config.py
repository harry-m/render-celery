import sys
import os
from celery import Celery, signals
from celery.schedules import crontab 
from celery_task_base import DatabaseTask
from database import TaskCache, database as db
from sqlalchemy import func
import pkgutil
import importlib
import scheduled_tasks  # Import the package

# Ensure the "tasks" directory is in Python's module search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

celery = Celery('soom', broker=os.getenv("CELERY_BROKER_URL"))
celery.Task = DatabaseTask

celery.autodiscover_tasks(["tasks"])

# Catch tasks when they are submitted and save them
@signals.task_prerun.connect
def task_start_handler(sender=None, task_id=None, task=None, **kwargs):
    # Add task id to the task_cache table
    params = {
        "id": task_id, 
        "task_name": sender.name, 
        "parameters": kwargs['args'],
        "submitted_at": func.now()
    }

    new_task = TaskCache(**params)

    db.session.add(new_task)
    db.session.commit()
    
    # This function is called every time any task is about to run.
    print(f"Task {task}, sent by {sender.name} with id {task_id} is starting: {kwargs}.")

for finder, module_name, is_pkg in pkgutil.iter_modules(scheduled_tasks.__path__):
    module = importlib.import_module(f"scheduled_tasks.{module_name}")
    if hasattr(module, 'schedule'):
        sched = module.schedule
        # Use the 'name' field as the key in beat_schedule
        celery.conf.beat_schedule[sched['name']] = sched
