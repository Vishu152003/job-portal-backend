#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create admin user if not exists
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )
    admin.role = 'admin'
    admin.save()
    print("✅ Admin user created successfully!")
else:
    print("ℹ️ Admin user already exists")

print(f"Total users: {User.objects.count()}")
