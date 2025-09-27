import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates an admin user non-interactively from environment variables'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USER')
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING('Skipping superuser creation: ADMIN_USER, ADMIN_EMAIL, and ADMIN_PASSWORD are required.'))
            return

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Creating account for {username} ({email})')
            User.objects.create_superuser(email=email, username=username, password=password)
            self.stdout.write(self.style.SUCCESS('Admin user created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))