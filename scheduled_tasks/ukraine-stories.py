from datetime import timedelta

test_schedule = {
    'name': 'daily-summary-of-url',
    'task': 'tasks.summarise_url.summarise_url',
    'schedule': timedelta(hours=24),
    'args': ('https://www.bbc.co.uk/news', 'Include all stories about Ukraine'),
}
