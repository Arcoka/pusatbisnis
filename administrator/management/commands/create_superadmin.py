from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Membuat user superadmin baru'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username untuk superadmin')
        parser.add_argument('email', type=str, help='Email untuk superadmin')
        parser.add_argument('password', type=str, help='Password untuk superadmin')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            # Cek apakah user sudah ada
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.ERROR(f'User dengan username "{username}" sudah ada!')
                )
                return

            # Buat user baru
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Buat profil admin panel dengan status superadmin
            AdminPanelUser.objects.create(
                user=user,
                is_superadmin=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Superadmin "{username}" berhasil dibuat!\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Status: Superadmin'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )