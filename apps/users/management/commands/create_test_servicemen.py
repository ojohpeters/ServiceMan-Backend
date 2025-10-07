from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.services.models import Category
from apps.users.models import ServicemanProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test servicemen and assign them to categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category-id',
            type=int,
            help='Category ID to assign servicemen to',
            default=1
        )

    def handle(self, *args, **options):
        category_id = options['category_id']
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Category with ID {category_id} does not exist')
            )
            return

        # Create test servicemen
        test_servicemen = [
            {
                'username': 'john_electrician',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'bio': 'Experienced electrician with 10+ years in residential and commercial electrical work.',
                'years_of_experience': 10,
                'phone_number': '+2348012345678'
            },
            {
                'username': 'jane_electrician',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'bio': 'Professional electrician specializing in smart home installations and electrical repairs.',
                'years_of_experience': 8,
                'phone_number': '+2348012345679'
            },
            {
                'username': 'mike_electrician',
                'email': 'mike@example.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'bio': 'Licensed electrician with expertise in industrial electrical systems and emergency repairs.',
                'years_of_experience': 12,
                'phone_number': '+2348012345680'
            }
        ]

        created_count = 0
        for serviceman_data in test_servicemen:
            # Check if user already exists
            if User.objects.filter(email=serviceman_data['email']).exists():
                self.stdout.write(
                    self.style.WARNING(f'Serviceman {serviceman_data["email"]} already exists, skipping...')
                )
                continue

            # Create user
            user = User.objects.create_user(
                username=serviceman_data['username'],
                email=serviceman_data['email'],
                password='TestPass123!',
                user_type='SERVICEMAN',
                first_name=serviceman_data['first_name'],
                last_name=serviceman_data['last_name']
            )

            # Update serviceman profile
            profile = user.serviceman_profile
            profile.category = category
            profile.bio = serviceman_data['bio']
            profile.years_of_experience = serviceman_data['years_of_experience']
            profile.phone_number = serviceman_data['phone_number']
            profile.rating = 4.5 + (created_count * 0.1)  # Vary ratings slightly
            profile.total_jobs_completed = 20 + (created_count * 5)  # Vary job counts
            profile.save()

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created serviceman: {user.get_full_name()} ({user.email})')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} servicemen assigned to category "{category.name}"')
        )

        # Show current servicemen in category
        servicemen_in_category = User.objects.filter(
            user_type='SERVICEMAN',
            serviceman_profile__category_id=category_id
        )
        
        self.stdout.write(f'\nServicemen in category "{category.name}" (ID: {category_id}):')
        for serviceman in servicemen_in_category:
            profile = serviceman.serviceman_profile
            self.stdout.write(f'- {serviceman.get_full_name()} (Rating: {profile.rating}, Jobs: {profile.total_jobs_completed})')
