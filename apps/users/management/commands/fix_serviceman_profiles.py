"""
Management command to create missing ServicemanProfile objects.

Run with: python manage.py fix_serviceman_profiles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import ServicemanProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create missing ServicemanProfile objects for users with user_type=SERVICEMAN'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Checking for servicemen without profiles...'))
        
        # Find all SERVICEMAN users
        servicemen = User.objects.filter(user_type='SERVICEMAN')
        total_servicemen = servicemen.count()
        self.stdout.write(f'Found {total_servicemen} users with user_type=SERVICEMAN')
        
        # Check which ones are missing profiles
        missing_profiles = []
        for user in servicemen:
            if not hasattr(user, 'serviceman_profile'):
                missing_profiles.append(user)
        
        if not missing_profiles:
            self.stdout.write(self.style.SUCCESS('✓ All servicemen have profiles!'))
            return
        
        self.stdout.write(
            self.style.WARNING(
                f'Found {len(missing_profiles)} servicemen WITHOUT profiles:'
            )
        )
        
        for user in missing_profiles:
            self.stdout.write(f'  - User ID {user.id}: {user.username} ({user.email})')
        
        # Ask for confirmation
        confirm = input('\nCreate profiles for these users? (yes/no): ')
        
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Aborted.'))
            return
        
        # Create missing profiles
        created_count = 0
        for user in missing_profiles:
            try:
                profile = ServicemanProfile.objects.create(
                    user=user,
                    bio='',
                    years_of_experience=0,
                    phone_number='',
                    is_available=True,
                    rating=0.00,
                    total_jobs_completed=0,
                    is_approved=False  # New servicemen should be approved by admin
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created profile for {user.username} (ID: {user.id})'
                    )
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to create profile for {user.username}: {e}'
                    )
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Successfully created {created_count} serviceman profiles!'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Note: New profiles have is_approved=False'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '   Admin should review and approve them at /api/users/admin/pending-servicemen/'
            )
        )

