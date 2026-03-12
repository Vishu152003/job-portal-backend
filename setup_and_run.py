import os
import sys

# Add the backend directory to the path so Python can find the jobportal module
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')

# Change to backend directory
os.chdir(backend_dir)

# Import Django and setup
import django
django.setup()

# Run migrations first
print("Running migrations...")
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate'])

print("\n" + "="*50)
print("Migrations complete!")
print("="*50 + "\n")

# Now run daphne
print("Starting server...")
from daphne.cli import CLI
sys.argv = ['daphne', '-b', '127.0.0.1', '-p', '8000', 'jobportal.asgi:application']
CLI().run()
