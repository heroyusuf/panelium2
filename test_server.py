import requests
import time
import subprocess

p = subprocess.Popen(["python3", "editor_server.py"])
time.sleep(1)

try:
    print(requests.get('http://localhost:8000/editor.html').status_code)
    print(requests.get('http://localhost:8000/pannellum.css').status_code)
    print(requests.get('http://localhost:8000/pannellum.js').status_code)
    print(requests.get('http://localhost:8000/list_icons').status_code)
    print(requests.get('http://localhost:8000/config.json?t=123').status_code)
    print(requests.get('http://localhost:8000/favicon.ico').status_code)
except Exception as e:
    print(e)

p.terminate()
