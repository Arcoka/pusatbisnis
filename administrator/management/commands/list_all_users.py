from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Menampilkan semua user dan status admin mereka'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Daftar Semua User ==='))
        
        django_users = User.objects.all()
        self.stdout.write(f'\nTotal User Django: {django_users.count()}')
        
        for user in django_users:
            self.stdout.write(f'\n--- {user.username} ---')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Is Active: {user.is_active}')
            self.stdout.write(f'Is Staff: {user.is_staff}')
            self.stdout.write(f'Is Superuser: {user.is_superuser}')
            
            try:
                admin_profile = user.admin_panel_profile
                status = 'Superadmin' if admin_profile.is_superadmin else 'Admin'
                self.stdout.write(f'Admin Status: {status}')
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.WARNING('Admin Status: Tidak memiliki profil admin'))
        
        admin_users = AdminPanelUser.objects.select_related('user').all()
        self.stdout.write(f'\n=== User dengan Profil Admin ({admin_users.count()}) ===')
        
        for admin_user in admin_users:
            status = 'Superadmin' if admin_user.is_superadmin else 'Admin'
            self.stdout.write(f'- {admin_user.user.username}: {status}') 