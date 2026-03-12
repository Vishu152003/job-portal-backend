from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates an admin user for the job portal'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')

    def handle(self, *args, **options):
        username = options.get('username') or 'admin'
        email = options.get('email') or 'admin@jobportal.com'
        password = options.get('password') or 'admin123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists!'))
            # Make existing user an admin
            user = User.objects.get(username=username)
            user.role = 'admin'
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated {username} to admin!'))
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin',
                is_superuser=True,
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS(f'Admin user {username} created successfully!'))
        
        self.stdout.write(self.style.SUCCESS(f'\nLogin credentials:'))
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'\nURL: http://localhost:5173/login')
