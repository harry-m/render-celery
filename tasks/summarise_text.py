from openai import OpenAI

from task_utils import send_to_llm
from celery_config import celery

@celery.task
def summarise_text(text:str, additional_prompt:str=""):
    return send_to_llm(text, "" + additional_prompt)

def summarise_text_template():
    return """
        <form action="/task/summarise_text" method="POST" class="p-4 border rounded">
            <div class="form-group">
                <label for="text">Text:</label>
                <textarea id="text" name="text" class="form-control" rows="5"></textarea>
            </div>
            <div class="form-group">
                <label for="additional_prompt">Additional prompt:</label>
                <textarea id="additional_prompt" name="additional_prompt" class="form-control" rows="2"></textarea>
            </div>
            <div class="form-group">
                <input type="hidden" name="format" value="html">
                <button type="submit" name="action" value="Run" class="btn btn-primary">Run</button>
                <button type="submit" name="action" value="Enqueue" class="btn btn-secondary">Enqueue</button>
            </div>
        </form>
    """