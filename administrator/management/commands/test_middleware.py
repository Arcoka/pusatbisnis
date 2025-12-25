from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser
from administrator.middleware import AdminPanelAccessMiddleware

class Command(BaseCommand):
    help = 'Menguji middleware AdminPanelAccessMiddleware'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diuji')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'\n=== Test Middleware untuk User: {username} ===')
            
            # Cek profil admin
            try:
                admin_profile = user.admin_panel_profile
                self.stdout.write(f'Has Admin Profile: Yes')
                self.stdout.write(f'Is Superadmin: {admin_profile.is_superadmin}')
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.WARNING('Has Admin Profile: No'))
                return
            
            # Test middleware dengan berbagai path
            factory = RequestFactory()
            middleware = AdminPanelAccessMiddleware(lambda request: 'OK')
            
            test_paths = [
                '/administrator/',
                '/administrator/users/',
                '/administrator/users/add/',
                '/administrator/users/1/edit/',
                '/administrator/users/1/delete/',
                '/admin/',  # Path yang tidak seharusnya diintervensi
                '/',  # Path yang tidak seharusnya diintervensi
            ]
            
            for path in test_paths:
                self.stdout.write(f'\n--- Testing Path: {path} ---')
                request = factory.get(path)
                request.user = user
                
                try:
                    response = middleware(request)
                    if hasattr(response, 'url'):
                        self.stdout.write(f'Redirected to: {response.url}')
                    else:
                        self.stdout.write(f'Response: {response}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 