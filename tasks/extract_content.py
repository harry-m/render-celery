import requests
from bs4 import BeautifulSoup

from task_utils import send_to_llm
from celery_config import celery

@celery.task
def extract_content(url:str, ai_cleanup:bool=False):
    # Fetch the page at the given URL
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes

    # Extract the text content from the response
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Attempt to find the main content of the page
    main_content = soup.find('main')
    if not main_content:
      main_content = soup.find('article')
    if not main_content:
      main_content = soup.find('div', {'id': 'content'})
    if not main_content:
      main_content = soup.find('div', {'class': 'content'})
    if not main_content:
      main_content = soup.find('div', {'role': 'main'})
    if not main_content:
      main_content = soup.find('section')
    if not main_content:
      main_content = soup.find('div', {'class': 'main-content'})
    if not main_content:
      main_content = soup.body

    # Extract text from the main content
    text = main_content.get_text(separator='\n', strip=True)

    if ai_cleanup:
      return send_to_llm(text, "The following text is an article, but it contains stuff that I don't want, like the publication date, related content, comments, and similar. Please remove this mess, returning the rest of the article unchanged.")

    return text

def extract_content_template():
    return """
        <form action="/task/extract_content" method="POST" class="p-4 border rounded">
            <div class="form-group">
                <label for="url">URL:</label>
                <input type="text" id="url" name="url" class="form-control">
            </div>
            <div class="form-group">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" id="ai_cleanup" name="ai_cleanup">
                <label class="form-check-label" for="ai_cleanup">
                  Tidy up the returned text with an LLM
                </label>
              </div>
            </div>
            <div class="form-group">
                <input type="hidden" name="format" value="html">
                <button type="submit" name="action" value="Run" class="btn btn-primary">Run</button>
                <button type="submit" name="action" value="Enqueue" class="btn btn-secondary">Enqueue</button>
            </div>
        </form>
    """