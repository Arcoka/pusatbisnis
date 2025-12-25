from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Memperbaiki semua user yang tidak memiliki profil admin'

    def add_arguments(self, parser):
        parser.add_argument('--make-superadmin', action='store_true', help='Buat semua user menjadi superadmin')
        parser.add_argument('--make-admin', action='store_true', help='Buat semua user menjadi admin biasa')

    def handle(self, *args, **options):
        django_users = User.objects.all()
        fixed_count = 0
        
        self.stdout.write(self.style.SUCCESS('=== Memperbaiki User Tanpa Profil Admin ==='))
        
        for user in django_users:
            try:
                user.admin_panel_profile
                # User sudah memiliki profil admin
                self.stdout.write(f'✓ {user.username}: Sudah memiliki profil admin')
            except AdminPanelUser.DoesNotExist:
                # User tidak memiliki profil admin, buat baru
                is_superadmin = options['make_superadmin']
                AdminPanelUser.objects.create(
                    user=user,
                    is_superadmin=is_superadmin
                )
                status = 'Superadmin' if is_superadmin else 'Admin'
                self.stdout.write(f'✓ {user.username}: Dibuat profil {status}')
                fixed_count += 1
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nBerhasil memperbaiki {fixed_count} user!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nSemua user sudah memiliki profil admin.')
            ) 