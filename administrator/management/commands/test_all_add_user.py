from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser
from administrator.views import add_admin_user, check_superadmin_access, check_admin_access
from administrator.middleware import AdminPanelAccessMiddleware
from django.urls import reverse
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'Test semua komponen add user sekaligus'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diuji')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'\n=== TEST ALL ADD USER COMPONENTS untuk User: {username} ==='))
            
            # 1. Test profil admin
            self.stdout.write(f'\n1. TESTING ADMIN PROFILE')
            try:
                admin_profile = user.admin_panel_profile
                self.stdout.write(f'✓ Has Admin Profile: Yes')
                self.stdout.write(f'✓ Is Superadmin: {admin_profile.is_superadmin}')
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.WARNING('✗ Has Admin Profile: No'))
                self.stdout.write(self.style.WARNING('Masalah: User tidak memiliki profil admin'))
                return
            
            # 2. Test fungsi akses
            self.stdout.write(f'\n2. TESTING ACCESS FUNCTIONS')
            can_superadmin = check_superadmin_access(user)
            can_admin = check_admin_access(user)
            self.stdout.write(f'check_superadmin_access: {can_superadmin}')
            self.stdout.write(f'check_admin_access: {can_admin}')
            
            if not can_superadmin:
                self.stdout.write(self.style.WARNING('Masalah: User tidak memiliki akses superadmin'))
            
            # 3. Test URL routing
            self.stdout.write(f'\n3. TESTING URL ROUTING')
            try:
                add_user_url = reverse('add_admin_user')
                self.stdout.write(f'✓ add_admin_user URL: {add_user_url}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error getting add_admin_user URL: {str(e)}'))
                self.stdout.write(self.style.WARNING('Masalah: URL routing tidak berfungsi'))
            
            # 4. Test middleware
            self.stdout.write(f'\n4. TESTING MIDDLEWARE')
            factory = RequestFactory()
            middleware = AdminPanelAccessMiddleware(lambda request: 'OK')
            
            request = factory.get('/administrator/users/add/')
            request.user = user
            
            try:
                response = middleware(request)
                if hasattr(response, 'url'):
                    self.stdout.write(f'✗ Middleware redirected to: {response.url}')
                    self.stdout.write(self.style.WARNING('Masalah: Middleware memblokir akses'))
                else:
                    self.stdout.write(f'✓ Middleware allowed access')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Middleware error: {str(e)}'))
            
            # 5. Test view function
            self.stdout.write(f'\n5. TESTING VIEW FUNCTION')
            request = factory.get('/administrator/users/add/')
            request.user = user
            
            try:
                response = add_admin_user(request)
                if hasattr(response, 'url'):
                    self.stdout.write(f'✗ View redirected to: {response.url}')
                    self.stdout.write(self.style.WARNING('Masalah: View memblokir akses'))
                else:
                    self.stdout.write(f'✓ View returned response with status: {response.status_code}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ View error: {str(e)}'))
            
            # 6. Test template rendering
            self.stdout.write(f'\n6. TESTING TEMPLATE RENDERING')
            try:
                context = {
                    'can_edit_superadmin': True,
                    'user': None
                }
                rendered = render_to_string('add_user.html', context)
                self.stdout.write(f'✓ Template add_user.html berhasil di-render')
                
                if 'method="post"' in rendered:
                    self.stdout.write(f'✓ Form ditemukan dalam template')
                else:
                    self.stdout.write(self.style.WARNING('✗ Form tidak ditemukan dalam template'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error rendering template: {str(e)}'))
            
            # 7. Kesimpulan dan solusi
            self.stdout.write(f'\n7. CONCLUSION')
            issues_found = []
            
            if not admin_profile.is_superadmin:
                issues_found.append("User bukan superadmin")
            if not can_superadmin:
                issues_found.append("User tidak memiliki akses superadmin")
            
            if issues_found:
                self.stdout.write(self.style.WARNING('Masalah yang ditemukan:'))
                for issue in issues_found:
                    self.stdout.write(f'  - {issue}')
                
                self.stdout.write(f'\n🔧 SOLUSI:')
                self.stdout.write('Jalankan command berikut untuk memperbaiki:')
                self.stdout.write(f'  python manage.py quick_fix_add_user {username}')
            else:
                self.stdout.write(self.style.SUCCESS('✓ Semua komponen berfungsi dengan baik'))
                self.stdout.write('Jika masih ada masalah, periksa:')
                self.stdout.write('  - Console browser untuk error JavaScript')
                self.stdout.write('  - Log server Django')
                self.stdout.write('  - Network tab di browser developer tools')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 