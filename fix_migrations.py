import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')

# Setup Django
import django
django.setup()

from django.db import connection

# Delete chat migration records
cursor = connection.cursor()
cursor.execute("DELETE FROM django_migrations WHERE app = 'chat'")
print('Chat migration records deleted')

# Now run migrations
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate'])
