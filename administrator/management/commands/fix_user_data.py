from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Memperbaiki data user yang hilang dan menampilkan status user'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='Memperbaiki data user yang hilang')
        parser.add_argument('--list', action='store_true', help='Menampilkan daftar semua user')

    def handle(self, *args, **options):
        if options['list']:
            self.list_users()
        elif options['fix']:
            self.fix_user_data()
        else:
            self.stdout.write(self.style.WARNING('Gunakan --list untuk melihat user atau --fix untuk memperbaiki data'))

    def list_users(self):
        """Menampilkan daftar semua user"""
        self.stdout.write(self.style.SUCCESS('=== Daftar Semua User ==='))
        
        # User Django
        django_users = User.objects.all()
        self.stdout.write(f'\nUser Django ({django_users.count()}):')
        for user in django_users:
            self.stdout.write(f'  - {user.username} ({user.email})')
        
        # Admin Panel Users
        admin_users = AdminPanelUser.objects.select_related('user').all()
        self.stdout.write(f'\nAdmin Panel Users ({admin_users.count()}):')
        for admin_user in admin_users:
            status = 'Superadmin' if admin_user.is_superadmin else 'Admin'
            self.stdout.write(f'  - {admin_user.user.username} ({status})')
        
        # User tanpa profil admin
        users_without_profile = []
        for user in django_users:
            try:
                user.admin_panel_profile
            except AdminPanelUser.DoesNotExist:
                users_without_profile.append(user)
        
        if users_without_profile:
            self.stdout.write(f'\nUser tanpa profil admin ({len(users_without_profile)}):')
            for user in users_without_profile:
                self.stdout.write(f'  - {user.username} (perlu dibuat profil admin)')

    def fix_user_data(self):
        """Memperbaiki data user yang hilang"""
        self.stdout.write(self.style.SUCCESS('=== Memperbaiki Data User ==='))
        
        # Cari user Django yang tidak punya profil admin
        django_users = User.objects.all()
        fixed_count = 0
        
        for user in django_users:
            try:
                user.admin_panel_profile
            except AdminPanelUser.DoesNotExist:
                # Buat profil admin untuk user ini
                AdminPanelUser.objects.create(
                    user=user,
                    is_superadmin=False  # Default sebagai admin biasa
                )
                self.stdout.write(f'✓ Membuat profil admin untuk {user.username}')
                fixed_count += 1
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nBerhasil memperbaiki {fixed_count} user!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nTidak ada user yang perlu diperbaiki.')
            ) 