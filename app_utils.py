from flask import flash, jsonify, render_template, redirect, url_for
from types import SimpleNamespace
import inspect
from urllib.parse import urlencode


def send_result(result, format, template=None):
    if format == "html":
        if not template:
            raise ValueError("Template is required for HTML format")
        
        return render_template(template, result=result)
    
    if format == "json":
        return jsonify(result=result)
    
    if format == "plain":
        return result
    
def send_message(message, format, category):
    if format == "html":
        flash(message, category)
        return redirect("/")
    
    if format == "json":
        return jsonify(result='', message=message, category=category)
    
    if format == "plain":
        return f"{category}: {message}"
    
def format_apicall_url_params(function):
    sig = inspect.signature(function)
    
    usage = SimpleNamespace(
        querystr="",
        json= "{ "
    )

    for name, param in sig.parameters.items():
      param_type = param.annotation.__name__ if param.annotation != inspect._empty else None

      if param.default != inspect._empty:
        usage.querystr += f"[&{name}=<{param.default}:{param_type}>]"
      else:
        usage.querystr += f"&{name}=<{param_type}>"

      usage.json += f"{name}: \"{param_type}\", "
    
    usage.json = usage.json.rstrip(', ')
    usage.json += " }"

    usage.querystr = usage.querystr.lstrip('&')
    
    return usage
  

