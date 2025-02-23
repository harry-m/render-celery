from celery_config import celery
from sqlalchemy.orm import Session
from database import database as db


@celery.task
def fetch_result(task_id:str):
    session = Session(bind=db.engine)
    try:
      task = session.query(TaskCache).filter(TaskCache.id == task_id).one()
    finally:
      session.close()

    if not task:
        raise ValueError(f"Task {task_id} not found")
        return None
    
    return task.result

def fetch_result_template():
    return """
        <form action="/task/fetch_result" method="POST" class="p-4 border rounded">
            <div class="form-group">
                <label for="url">Task ID:</label>
                <input type="text" id="task_id" name="task_id" class="form-control">
            </div>
           
            <div class="form-group">
                <input type="hidden" name="format" value="html">
                <button type="submit" name="action" value="Run" class="btn btn-primary">Run</button>
            </div>
        </form>
    """