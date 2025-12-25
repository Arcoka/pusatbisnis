from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Mengubah user menjadi superadmin'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username user yang akan diubah menjadi superadmin')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            
            # Cek apakah user sudah memiliki profil admin
            try:
                admin_profile = user.admin_panel_profile
                admin_profile.is_superadmin = True
                admin_profile.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'User "{username}" berhasil diubah menjadi superadmin!'
                    )
                )
            except AdminPanelUser.DoesNotExist:
                # Buat profil admin baru dengan status superadmin
                AdminPanelUser.objects.create(
                    user=user,
                    is_superadmin=True
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'User "{username}" berhasil dibuat profil admin dengan status superadmin!'
                    )
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User dengan username "{username}" tidak ditemukan!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 