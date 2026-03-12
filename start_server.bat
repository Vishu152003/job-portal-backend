@echo off
cd /d "%~dp0"
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings'); import django; django.setup(); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])"
echo.
echo Starting server...
python -m daphne -b 127.0.0.1 -p 8000 jobportal.asgi:application
