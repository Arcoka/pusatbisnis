from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Memperbaiki masalah add user secara otomatis'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diperbaiki')
        parser.add_argument('--make-superadmin', action='store_true', help='Buat user menjadi superadmin')

    def handle(self, *args, **options):
        username = options['username']
        make_superadmin = options['make_superadmin']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'\n=== FIXING ADD USER ISSUE untuk User: {username} ==='))
            
            # 1. Cek dan perbaiki profil admin
            self.stdout.write(f'\n1. CHECKING AND FIXING ADMIN PROFILE')
            try:
                admin_profile = user.admin_panel_profile
                self.stdout.write(f'✓ User sudah memiliki profil admin')
                
                if make_superadmin and not admin_profile.is_superadmin:
                    admin_profile.is_superadmin = True
                    admin_profile.save()
                    self.stdout.write(self.style.SUCCESS('✓ User berhasil diubah menjadi superadmin'))
                elif admin_profile.is_superadmin:
                    self.stdout.write(f'✓ User sudah menjadi superadmin')
                else:
                    self.stdout.write(self.style.WARNING('User bukan superadmin. Gunakan --make-superadmin untuk mengubah'))
                    
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.WARNING('✗ User tidak memiliki profil admin, membuat profil baru...'))
                
                # Buat profil admin baru
                is_superadmin = make_superadmin
                AdminPanelUser.objects.create(
                    user=user,
                    is_superadmin=is_superadmin
                )
                status = 'Superadmin' if is_superadmin else 'Admin'
                self.stdout.write(self.style.SUCCESS(f'✓ Profil admin berhasil dibuat dengan status: {status}'))
            
            # 2. Verifikasi perbaikan
            self.stdout.write(f'\n2. VERIFYING FIX')
            try:
                admin_profile = user.admin_panel_profile
                self.stdout.write(f'✓ Has Admin Profile: Yes')
                self.stdout.write(f'✓ Is Superadmin: {admin_profile.is_superadmin}')
                
                if admin_profile.is_superadmin:
                    self.stdout.write(self.style.SUCCESS('✓ User sekarang dapat mengakses halaman add user'))
                else:
                    self.stdout.write(self.style.WARNING('⚠ User masih bukan superadmin, tidak dapat menambah user'))
                    
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.ERROR('✗ Masih ada masalah dengan profil admin'))
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 