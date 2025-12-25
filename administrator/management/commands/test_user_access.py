from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser
from administrator.views import check_superadmin_access, check_admin_access

class Command(BaseCommand):
    help = 'Menguji akses user ke halaman tertentu'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diuji')
        parser.add_argument('--test-add-user', action='store_true', help='Test akses ke add user')
        parser.add_argument('--test-edit-user', action='store_true', help='Test akses ke edit user')
        parser.add_argument('--test-delete-user', action='store_true', help='Test akses ke delete user')
        parser.add_argument('--test-view-users', action='store_true', help='Test akses ke view users')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'\n=== Test Akses untuk User: {username} ===')
            
            # Cek profil admin
            try:
                admin_profile = user.admin_panel_profile
                self.stdout.write(f'Has Admin Profile: Yes')
                self.stdout.write(f'Is Superadmin: {admin_profile.is_superadmin}')
            except AdminPanelUser.DoesNotExist:
                self.stdout.write(self.style.WARNING('Has Admin Profile: No'))
                return
            
            # Test fungsi akses
            if options['test_add_user']:
                can_add = check_superadmin_access(user)
                self.stdout.write(f'Can Add User: {can_add}')
            
            if options['test_edit_user']:
                can_edit = check_admin_access(user)
                self.stdout.write(f'Can Edit User: {can_edit}')
            
            if options['test_delete_user']:
                can_delete = check_superadmin_access(user)
                self.stdout.write(f'Can Delete User: {can_delete}')
            
            if options['test_view_users']:
                can_view = check_admin_access(user)
                self.stdout.write(f'Can View Users: {can_view}')
            
            if not any([options['test_add_user'], options['test_edit_user'], 
                       options['test_delete_user'], options['test_view_users']]):
                # Test semua akses
                self.stdout.write(f'Can Add User: {check_superadmin_access(user)}')
                self.stdout.write(f'Can Edit User: {check_admin_access(user)}')
                self.stdout.write(f'Can Delete User: {check_superadmin_access(user)}')
                self.stdout.write(f'Can View Users: {check_admin_access(user)}')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 