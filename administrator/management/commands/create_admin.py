from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from models import AdminPanelUser
from setup_admin import create_admin_groups

class Command(BaseCommand):
    help = 'Membuat user admin biasa untuk admin panel'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Buat grup admin
        admin_group, superadmin_group = create_admin_groups()
        
        # Buat user django
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(f'User {username} sudah ada, mengupdate...')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_active=True
            )
            self.stdout.write(f'User {username} berhasil dibuat')
        
        # Buat admin panel profile
        admin_profile, created = AdminPanelUser.objects.get_or_create(
            user=user,
            defaults={'is_superadmin': False}
        )
        
        if not created:
            admin_profile.is_superadmin = False
            admin_profile.save()
        
        # Tambahkan ke grup admin
        user.groups.add(admin_group)
        
        self.stdout.write(self.style.SUCCESS(f'Admin {username} berhasil dibuat atau diupdate'))