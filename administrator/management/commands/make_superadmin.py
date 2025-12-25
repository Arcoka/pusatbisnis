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
            # Cari user
            user = User.objects.get(username=username)
            
            # Buat atau update profil admin panel
            admin_profile, created = AdminPanelUser.objects.get_or_create(
                user=user,
                defaults={'is_superadmin': True}
            )
            
            if not created:
                admin_profile.is_superadmin = True
                admin_profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'User "{username}" berhasil diubah menjadi superadmin!'
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