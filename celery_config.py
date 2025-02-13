import sys
import os
from celery import Celery
from celery_task_base import DatabaseTask


# Ensure the "tasks" directory is in Python's module search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

celery = Celery('soom', broker=os.getenv("CELERY_BROKER_URL"))
celery.Task = DatabaseTask

celery.autodiscover_tasks(["tasks"])
