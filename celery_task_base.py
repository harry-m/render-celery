from celery import Task
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database import database as db 
from models import TaskCache 

class DatabaseTask(Task):
    _session = None  # Lazy-initialized database session

    def __call__(self, *args, **kwargs):
        # Override __call__ to execute the task
        result = super().__call__(*args, **kwargs) 
        
        # Save the result to the database
        self.save_result(self.request.id, result)

        return result

    def save_result(self, task_id, result):
        if not self._session:
            # Lazy initialization
            self._session = scoped_session(sessionmaker(bind=db.engine))  
         
        # Find the original task entry
        task_entry = self._session.query(TaskCache).get(task_id)
        
        if not task_entry:
            raise NoResultFound(f"Task {task_id} not found, cannot save result")

        # Update task result and mark as finished
        task_entry.result = result
        task_entry.finished_at = db.func.now()

        self._session.commit()

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # Clean up database session
        if self._session:
            self._session.remove()
