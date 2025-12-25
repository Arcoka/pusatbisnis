from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser
from administrator.views import check_superadmin_access

class Command(BaseCommand):
    help = 'Auto fix untuk masalah add user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diperbaiki')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'\n=== AUTO FIX ADD USER untuk User: {username} ==='))
            
            # 1. Diagnosa masalah
            self.stdout.write(f'\n1. DIAGNOSING...')
            
            has_profile = True
            is_superadmin = False
            try:
                admin_profile = user.admin_panel_profile
                is_superadmin = admin_profile.is_superadmin
                self.stdout.write(f'✓ Has Admin Profile: Yes')
                self.stdout.write(f'✓ Is Superadmin: {is_superadmin}')
            except AdminPanelUser.DoesNotExist:
                has_profile = False
                self.stdout.write(self.style.WARNING('✗ Has Admin Profile: No'))
            
            can_superadmin = check_superadmin_access(user)
            self.stdout.write(f'✓ Can Add User: {can_superadmin}')
            
            # 2. Identifikasi masalah
            issues = []
            if not has_profile:
                issues.append("Tidak memiliki profil admin")
            if not is_superadmin:
                issues.append("Bukan superadmin")
            if not can_superadmin:
                issues.append("Tidak memiliki akses superadmin")
            
            if not issues:
                self.stdout.write(self.style.SUCCESS('✓ User sudah dapat menambah user'))
                return
            
            # 3. Perbaiki masalah
            self.stdout.write(f'\n2. FIXING ISSUES...')
            
            if not has_profile:
                self.stdout.write('Membuat profil admin superadmin...')
                AdminPanelUser.objects.create(
                    user=user,
                    is_superadmin=True
                )
                self.stdout.write(self.style.SUCCESS('✓ Profil admin superadmin berhasil dibuat'))
            elif not is_superadmin:
                self.stdout.write('Mengubah user menjadi superadmin...')
                admin_profile.is_superadmin = True
                admin_profile.save()
                self.stdout.write(self.style.SUCCESS('✓ User berhasil diubah menjadi superadmin'))
            
            # 4. Verifikasi perbaikan
            self.stdout.write(f'\n3. VERIFYING FIXES...')
            try:
                admin_profile = user.admin_panel_profile
                can_superadmin = check_superadmin_access(user)
                
                self.stdout.write(f'✓ Has Admin Profile: Yes')
                self.stdout.write(f'✓ Is Superadmin: {admin_profile.is_superadmin}')
                self.stdout.write(f'✓ Can Add User: {can_superadmin}')
                
                if can_superadmin:
                    self.stdout.write(self.style.SUCCESS('✓ Masalah berhasil diperbaiki!'))
                    self.stdout.write('Sekarang Anda dapat mengakses halaman "Tambah User"')
                else:
                    self.stdout.write(self.style.ERROR('✗ Masih ada masalah dengan akses'))
                    
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