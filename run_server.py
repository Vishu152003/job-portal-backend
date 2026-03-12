import os
import sys

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')

# Run migrations first
from django.core.management import execute_from_command_line
print("Running migrations...")
execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])

# Now run daphne
print("\nStarting server with daphne...")
from daphne.cli import CLI
sys.argv = ['daphne', '-b', '127.0.0.1', '-p', '8000', 'jobportal.asgi:application']
CLI().run()
