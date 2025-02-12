import os
from flask import Flask, render_template, request
from sqlalchemy import create_engine, Table, Column, String, MetaData, UUID, func, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from flask_httpauth import HTTPBasicAuth

import tasks
from app_utils import *
from celery_config import celery
from database import database as db
from models import TaskCache



app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "sep897rugb04w57bg40957gb9pergbouerdbv.lxcnv,kdjfbgoeri6yutbgodznyujxikcisgrfbgdsvabolisj")
auth = HTTPBasicAuth()

# Configure database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Simulated user database
users = {
    "admin": os.getenv('ADMIN_PASSWORD'),
}


@auth.verify_password
def verify_password(username, password):
    """Verify username and password."""
    if username in users and users[username] == password:
        return username  # Authenticated user
    return None  # Authentication failed


@app.route('/')
@auth.login_required
def main():
    available_tasks = []

    for task in celery.tasks.keys():
        if not task.startswith('task'):
            continue

        task_name = task.split('.')[-1]
        task_handler = getattr(getattr(tasks, task_name), task_name)

        available_tasks.append({
            "name": task_name,
            "title": task_name.replace('_', ' ').title(),
            "handler": task_handler,
            "template": getattr(getattr(tasks, task_name), f"{task_name}_template"),
            "url_path": url_for('run_task', name=task_name, _external=True),
            "url_params": format_apicall_url_params(task_handler)
        })

    return render_template('main.html', available_tasks=available_tasks)


@app.route('/task/<name>', methods=['POST'])
@auth.login_required
def run_task(name):
    # Get a format if one was specified, or default to HTML
    format = request.form.get('format')

    if not format:
        format = "plain"

    if format not in ['plain', 'html', 'json']:
        return send_message("Invalid format", format, "error")
    

    # Check that we have a run or enqueue action
    action = request.form.get('action')

    if not action:
        action = "Run"
        
    if action not in ['Run', 'Enqueue']:
        return send_message("Invalid or missing action", format, "error")
    

    # Check if the function exists in the tasks module
    if not hasattr(tasks, name):
        return send_message(f"Task not found", format, "error")

    task_function = getattr(getattr(tasks, name), name)


    # Ensure it's actually a callable function
    if not callable(task_function):
        return send_message(f"'{name}' is not callable", format, "error")


    # Extract form parameters
    params = request.form.to_dict()
    params.pop('action', None)
    params.pop('format', None)


    # Enqueue or run the task, as directed
    try:
        if action == "Enqueue":
            queued_task = celery.send_task(name, kwargs=params)

            # Add task id to the task_cache table
            new_task = TaskCache(task_id=queued_task.id, task_name=name, parameters=params)
            db.session.add(new_task)
            db.session.commit()

            # # Create an engine and connect to the PostgreSQL database
            # engine = create_engine(os.getenv('DATABASE_URL'))
            # connection = engine.connect()
            # metadata = MetaData()

            # # Define the task_cache table
            # task_cache = Table('task_cache', metadata,
            #        Column('id', UUID(as_uuid=True), primary_key=True),
            #        Column('submitted_at', DateTime(timezone=True)),
            #        Column('finished_at', DateTime(timezone=True)),
            #        Column('task_name', String),
            #        Column('parameters', JSONB),
            #        Column('result', String)
            #     )

            # # Insert the task id and other details into the task_cache table
            # insert_query = task_cache.insert().values(
            #     id=uuid.UUID(queued_task.id),
            #     submitted_at=func.now(),
            #     task_name=name,
            #     parameters=params,
            #     result=''
            # )

            # # Ensure the transaction is committed
            # try:
            #     trans = connection.begin()  # Start a transaction
            #     connection.execute(insert_query)
            #     trans.commit()  # Commit the transaction

            # except Exception as e:
            #     trans.rollback()  # Rollback if there's an error

            #     return send_message(f"Unable to save task: {e}", format, "error")

            # finally:
            #     connection.close()  # Close connection

            return send_message("Your task has been enqueued", format, "info")
        
        else:
            # Call the function with form parameters
            task_result = task_function(**params)
            
            return send_result(task_result, format, 'result.html')
    
    
    # Handle exceptions
    except TypeError as e:
        return send_message(f"Invalid parameters: {str(e)}", format, "error")
    
    # except Exception as e:
    #     return send_message(f"run_task failed: {e}", format, "error")