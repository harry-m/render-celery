import os
import importlib
from pathlib import Path

TASKS_DIR = Path(__file__).parent

# Auto-import all Python files in the `tasks/` directory
for file in TASKS_DIR.glob("*.py"):
    if file.name == "__init__.py":
        continue  # Skip the init file
    
    module_name = f"tasks.{file.stem}"  # Convert filename to module name
    
    importlib.import_module(module_name)
