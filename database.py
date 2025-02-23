from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

import uuid

# Create a SQLAlchemy object
database = SQLAlchemy()

class TaskCache(database.Model):
    __tablename__ = "task_cache"

    id = database.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submitted_at = database.Column(database.DateTime(timezone=True), server_default=func.now())
    finished_at = database.Column(database.DateTime(timezone=True), nullable=True)
    task_name = database.Column(database.String, nullable=False)
    parameters = database.Column(JSONB, nullable=False)
    result = database.Column(database.String, nullable=True)

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            raise ValueError("Missing required argument 'id'")

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
