from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser
from administrator.views import add_admin_user, active_users, check_superadmin_access, check_admin_access

class Command(BaseCommand):
    help = 'Menguji fungsi view secara langsung'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diuji')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'\n=== Test Views untuk User: {username} ===')
            
            # Cek profil admin
            try:
                admin_profile = user.admin_panel_profile
                self.stdout.write(f'Has Admin Profile: Yes')
                self.stdout.write(f'Is Superadmin: {admin_profile.is_superadmin}')
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.WARNING('Has Admin Profile: No'))
                return
            
            # Test fungsi akses
            self.stdout.write(f'\n--- Test Access Functions ---')
            self.stdout.write(f'check_superadmin_access: {check_superadmin_access(user)}')
            self.stdout.write(f'check_admin_access: {check_admin_access(user)}')
            
            # Test view dengan request factory
            factory = RequestFactory()
            
            # Test add_admin_user view
            self.stdout.write(f'\n--- Test add_admin_user View ---')
            request = factory.get('/administrator/users/add/')
            request.user = user
            
            try:
                response = add_admin_user(request)
                self.stdout.write(f'Response status: {response.status_code}')
                if hasattr(response, 'url'):
                    self.stdout.write(f'Redirect URL: {response.url}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error in add_admin_user: {str(e)}'))
            
            # Test active_users view
            self.stdout.write(f'\n--- Test active_users View ---')
            request = factory.get('/administrator/users/')
            request.user = user
            
            try:
                response = active_users(request)
                self.stdout.write(f'Response status: {response.status_code}')
                if hasattr(response, 'url'):
                    self.stdout.write(f'Redirect URL: {response.url}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error in active_users: {str(e)}'))
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 