import requests
from bs4 import BeautifulSoup

from task_utils import send_to_llm
from celery_config import celery

@celery.task
def summarise_url(url:str, additional_prompt:str=""):
    # Fetch the page at the given URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Extract the text content from the response
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the plain text from the HTML
    text = soup.get_text()

    return send_to_llm(text, "Summarise the following text. " + additional_prompt)

def summarise_url_template():
    return """
        <form action="/task/summarise_url" method="POST" class="p-4 border rounded">
            <div class="form-group">
                <label for="url">URL:</label>
                <input type="text" id="url" name="url" class="form-control">
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