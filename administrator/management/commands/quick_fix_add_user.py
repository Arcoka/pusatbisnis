from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Quick fix untuk masalah add user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diperbaiki')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'\n=== QUICK FIX untuk User: {username} ==='))
            
            # Cek status saat ini
            try:
                admin_profile = user.admin_panel_profile
                if admin_profile.is_superadmin:
                    self.stdout.write(self.style.SUCCESS('✓ User sudah superadmin, tidak perlu perbaikan'))
                    return
                else:
                    self.stdout.write('User adalah admin biasa, mengubah menjadi superadmin...')
                    admin_profile.is_superadmin = True
                    admin_profile.save()
                    self.stdout.write(self.style.SUCCESS('✓ User berhasil diubah menjadi superadmin'))
            except AdminPanelUser.DoesNotExist:
                self.stdout.write('User tidak memiliki profil admin, membuat profil superadmin...')
                AdminPanelUser.objects.create(
                    user=user,
                    is_superadmin=True
                )
                self.stdout.write(self.style.SUCCESS('✓ Profil superadmin berhasil dibuat'))
            
            # Verifikasi
            admin_profile = user.admin_panel_profile
            self.stdout.write(f'\n✓ Status akhir:')
            self.stdout.write(f'  - Username: {user.username}')
            self.stdout.write(f'  - Is Superadmin: {admin_profile.is_superadmin}')
            self.stdout.write(f'  - Can Add User: Ya')
            
            self.stdout.write(self.style.SUCCESS('\n✓ Masalah add user sudah diperbaiki!'))
            self.stdout.write('Sekarang Anda dapat mengakses halaman "Tambah User"')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 