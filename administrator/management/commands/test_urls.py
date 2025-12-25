from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth.models import User
from administrator.models import AdminPanelUser

class Command(BaseCommand):
    help = 'Menguji URL routing untuk administrator'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Test URL Routing ==='))
        
        # Test URL patterns
        urls_to_test = [
            'active_users',
            'add_admin_user',
            'berandaadmin',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                self.stdout.write(f'✓ {url_name}: {url}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ {url_name}: Error - {str(e)}'))
        
        # Test dengan user dummy
        try:
            # Buat user dummy untuk testing
            user, created = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            
            if created:
                # Buat profil admin untuk user dummy
                AdminPanelUser.objects.create(
                    user=user,
                    is_superadmin=True
                )
                self.stdout.write('✓ Created test user')
            
            # Test request factory
            factory = RequestFactory()
            request = factory.get('/administrator/users/')
            request.user = user
            
            self.stdout.write(f'✓ Test request created for user: {user.username}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating test request: {str(e)}')) 