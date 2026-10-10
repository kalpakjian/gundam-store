"""Start the Django dev server in background, run smoke tests, then stop."""
import os
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error

os.environ['DJANGO_SETTINGS_MODULE'] = 'gundam_store.settings'
os.environ['SECRET_KEY'] = 'dev'
os.environ['DEBUG'] = 'True'
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, '.venv', 'Scripts', 'python.exe')

# Auto-load the bundled product fixture if the database is empty
print("Checking if product data needs to be loaded...")
subprocess.run(
    [BIN, 'manage.py', 'migrate', '--noinput'],
    cwd=HERE,
)
subprocess.run(
    [BIN, 'manage.py', 'loaddata_products'],
    cwd=HERE,
)

# Start server
proc = subprocess.Popen(
    [BIN, 'manage.py', 'runserver', '127.0.0.1:8000', '--noreload'],
    cwd=HERE,
    stdout=open(os.path.join(HERE, 'server.log'), 'w'),
    stderr=subprocess.STDOUT,
)

# Wait for server to be ready
base = 'http://127.0.0.1:8000'
print("Waiting for server...")
for i in range(50):
    try:
        urllib.request.urlopen(base + '/', timeout=1)
        print("Server is up!")
        break
    except Exception:
        time.sleep(0.2)
else:
    print("Server failed to start")
    proc.terminate()
    sys.exit(1)

# Run smoke tests
print("\n=== Smoke Tests ===")
paths = [
    '/', '/store/', '/store/products/', '/store/cart/', '/store/checkout/',
    '/accounts/login/', '/accounts/register/', '/admin/',
    '/store/orders/', '/store/share-images/', '/store/upload-image/',
    '/store/profile/', '/store/search/?q=gundam',
]

for path in paths:
    url = base + path
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.status_code
            body = r.read()
            print(f"  {code}  {path}  ({len(body)} bytes)")
    except urllib.error.HTTPError as e:
        print(f"  {e.code}  {path}  (HTTP error)")
    except Exception as e:
        print(f"  ERR  {path}  ({e})")

# Stop server
print("\nStopping server...")
proc.send_signal(signal.CTRL_BREAK_EVENT)
try:
    proc.wait(timeout=3)
except subprocess.TimeoutExpired:
    proc.kill()
print("Server stopped.")