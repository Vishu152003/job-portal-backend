import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')

# Setup Django and run migrations
import django
django.setup()

from django.core.management import execute_from_command_line

# Run migrations with --run-syncdb to create all tables
print("Running migrations with --run-syncdb...")
execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])

print("\nMigrations complete!")
print("\nTo start the server, run:")
print("python -m daphne -b 127.0.0.1 -p 8000 jobportal.asgi:application")
