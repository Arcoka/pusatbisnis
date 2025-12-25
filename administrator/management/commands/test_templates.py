from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Menguji template rendering'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diuji')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'\n=== Test Template Rendering untuk User: {username} ===')
            
            # Cek profil admin
            try:
                admin_profile = user.admin_panel_profile
                self.stdout.write(f'Has Admin Profile: Yes')
                self.stdout.write(f'Is Superadmin: {admin_profile.is_superadmin}')
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.WARNING('Has Admin Profile: No'))
                return
            
            # Test template add_user.html
            self.stdout.write(f'\n--- Test add_user.html Template ---')
            try:
                context = {
                    'can_edit_superadmin': True,
                    'user': None  # Untuk mode add user
                }
                rendered = render_to_string('add_user.html', context)
                self.stdout.write(f'✓ Template add_user.html berhasil di-render')
                self.stdout.write(f'Length: {len(rendered)} characters')
                
                # Cek apakah ada form dalam template
                if 'method="post"' in rendered:
                    self.stdout.write(f'✓ Form ditemukan dalam template')
                else:
                    self.stdout.write(self.style.WARNING('✗ Form tidak ditemukan dalam template'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error rendering add_user.html: {str(e)}'))
            
            # Test template user_list.html
            self.stdout.write(f'\n--- Test user_list.html Template ---')
            try:
                # Ambil data user untuk context
                admin_panel_users = AdminPanelUser.objects.select_related('user').all()
                users_with_profiles = [profile.user for profile in admin_panel_users]
                
                context = {
                    'users': users_with_profiles,
                    'admin_profiles': admin_panel_users,
                    'user': user,  # User yang sedang login
                }
                rendered = render_to_string('user_list.html', context)
                self.stdout.write(f'✓ Template user_list.html berhasil di-render')
                self.stdout.write(f'Length: {len(rendered)} characters')
                
                # Cek apakah ada link "Tambah User"
                if 'Tambah User' in rendered:
                    self.stdout.write(f'✓ Link "Tambah User" ditemukan')
                else:
                    self.stdout.write(self.style.WARNING('✗ Link "Tambah User" tidak ditemukan'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error rendering user_list.html: {str(e)}'))
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 