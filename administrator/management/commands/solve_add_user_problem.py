from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser
from administrator.views import add_admin_user, check_superadmin_access, check_admin_access
from administrator.middleware import AdminPanelAccessMiddleware
from django.urls import reverse

class Command(BaseCommand):
    help = 'Menyelesaikan masalah add user secara komprehensif'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diperbaiki')
        parser.add_argument('--fix', action='store_true', help='Perbaiki masalah secara otomatis')
        parser.add_argument('--make-superadmin', action='store_true', help='Buat user menjadi superadmin')

    def handle(self, *args, **options):
        username = options['username']
        fix = options['fix']
        make_superadmin = options['make_superadmin']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'\n=== SOLVING ADD USER PROBLEM untuk User: {username} ==='))
            
            # 1. Diagnosa masalah
            self.stdout.write(f'\n1. DIAGNOSING THE PROBLEM')
            
            # Cek profil admin
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
            
            # Test fungsi akses
            can_superadmin = check_superadmin_access(user)
            can_admin = check_admin_access(user)
            self.stdout.write(f'check_superadmin_access: {can_superadmin}')
            self.stdout.write(f'check_admin_access: {can_admin}')
            
            # Test URL routing
            url_ok = True
            try:
                add_user_url = reverse('add_admin_user')
                self.stdout.write(f'✓ add_admin_user URL: {add_user_url}')
            except Exception as e:
                url_ok = False
                self.stdout.write(self.style.ERROR(f'✗ Error getting add_admin_user URL: {str(e)}'))
            
            # 2. Identifikasi masalah
            self.stdout.write(f'\n2. IDENTIFYING ISSUES')
            issues = []
            
            if not has_profile:
                issues.append("User tidak memiliki profil admin panel")
            if not is_superadmin:
                issues.append("User bukan superadmin (diperlukan untuk menambah user)")
            if not url_ok:
                issues.append("Masalah dengan URL routing")
            if not can_superadmin:
                issues.append("User tidak memiliki akses superadmin")
            
            if issues:
                self.stdout.write(self.style.WARNING('Masalah yang ditemukan:'))
                for issue in issues:
                    self.stdout.write(f'  - {issue}')
            else:
                self.stdout.write(self.style.SUCCESS('✓ Tidak ada masalah yang ditemukan'))
            
            # 3. Solusi
            if fix and issues:
                self.stdout.write(f'\n3. APPLYING FIXES')
                
                # Perbaiki profil admin jika tidak ada
                if not has_profile:
                    self.stdout.write('Membuat profil admin...')
                    AdminPanelUser.objects.create(
                        user=user,
                        is_superadmin=make_superadmin
                    )
                    self.stdout.write(self.style.SUCCESS('✓ Profil admin berhasil dibuat'))
                
                # Ubah menjadi superadmin jika diminta
                elif not is_superadmin and make_superadmin:
                    admin_profile = user.admin_panel_profile
                    admin_profile.is_superadmin = True
                    admin_profile.save()
                    self.stdout.write(self.style.SUCCESS('✓ User berhasil diubah menjadi superadmin'))
                
                # Verifikasi perbaikan
                self.stdout.write(f'\n4. VERIFYING FIXES')
                try:
                    admin_profile = user.admin_panel_profile
                    self.stdout.write(f'✓ Has Admin Profile: Yes')
                    self.stdout.write(f'✓ Is Superadmin: {admin_profile.is_superadmin}')
                    
                    if admin_profile.is_superadmin:
                        self.stdout.write(self.style.SUCCESS('✓ User sekarang dapat mengakses halaman add user'))
                    else:
                        self.stdout.write(self.style.WARNING('⚠ User masih bukan superadmin'))
                        
                except AdminPanelUser.DoesNotExist:
                    self.stdout.write(self.style.ERROR('✗ Masih ada masalah dengan profil admin'))
            
            # 4. Instruksi manual jika tidak menggunakan --fix
            elif issues and not fix:
                self.stdout.write(f'\n3. MANUAL SOLUTIONS')
                self.stdout.write('Untuk memperbaiki masalah ini, jalankan salah satu command berikut:')
                
                if not has_profile:
                    self.stdout.write(f'  python manage.py fix_add_user_issue {username} --make-superadmin')
                elif not is_superadmin:
                    self.stdout.write(f'  python manage.py make_user_superadmin {username}')
                else:
                    self.stdout.write(f'  python manage.py debug_add_user {username}')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 