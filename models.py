import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import database as db

class TaskCache(db.Model):
    __tablename__ = "task_cache"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submitted_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    finished_at = db.Column(db.DateTime(timezone=True), nullable=True)
    task_name = db.Column(db.String, nullable=False)
    parameters = db.Column(JSONB, nullable=False)
    result = db.Column(db.String, nullable=True)

    def __init__(self, task_id, task_name, parameters):
        self.id = task_id
        self.task_name = task_name
        self.parameters = parameters
        self.submitted_at = func.now()
