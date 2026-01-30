from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from rides.models import User, Ride, RideEvent


class Command(BaseCommand):
    help = 'Seeds the database with sample data'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create users
        # Checks if admin exists first to avoid crashing if run twice
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='password',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            self.stdout.write('Created new admin user.')
        else:
            # Fix: If admin was created via createsuperuser, they might have default role='rider'
            # We force update it to 'admin' so API permissions work.
            admin = User.objects.get(username='admin')
            admin.role = 'admin'
            admin.save()
            self.stdout.write('Updated existing admin user role to "admin"')
        
        drivers = []
        for i, name in enumerate([('Chris', 'H'), ('Howard', 'Y'), ('Randy', 'W')]):
            driver = User.objects.create_user(
                username=f'driver{i}',
                email=f'{name[0].lower()}@wingz.com',
                password='password',
                first_name=name[0],
                last_name=name[1],
                role='driver'
            )
            drivers.append(driver)
        
        riders = []
        for i in range(5):
            rider = User.objects.create_user(
                username=f'rider{i}',
                email=f'rider{i}@example.com',
                password='password',
                first_name=f'Rider{i}',
                last_name='Test',
                role='rider'
            )
            riders.append(rider)
        
        # Create rides with events
        statuses = ['en-route', 'pickup', 'dropoff']
        for i in range(20):
            ride = Ride.objects.create(
                status=random.choice(statuses),
                id_rider=random.choice(riders),
                id_driver=random.choice(drivers),
                pickup_latitude=37.7749 + random.uniform(-0.1, 0.1),
                pickup_longitude=-122.4194 + random.uniform(-0.1, 0.1),
                dropoff_latitude=37.7849 + random.uniform(-0.1, 0.1),
                dropoff_longitude=-122.4294 + random.uniform(-0.1, 0.1),
                pickup_time=timezone.now() - timedelta(days=random.randint(0, 60))
            )
            
            # Create ride events
            for event_desc in ['Status changes to pickup', 'Status change to dropoff']:
                RideEvent.objects.create(
                    id_ride=ride,
                    description=event_desc,
                    created_at=timezone.now() - timedelta(hours=random.randint(0, 48))
                )
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))