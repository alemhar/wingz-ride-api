from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from rides.models import User, Ride, RideEvent

class Command(BaseCommand):
    help = 'Seeds data specifically for the 24h Trip Duration Report test'
    
    def handle(self, *args, **options):
        # ... (Copy the User creation logic from the other file) ...
        # OR just assume users exist if you ran the other seeder first.
        
        # Let's assume we fetch the first rider/driver to keep it simple
        rider = User.objects.filter(role='rider').first()
        driver = User.objects.filter(role='driver').first()
        
        if not rider or not driver:
            self.stdout.write(self.style.ERROR("Please run the main seed_data first to create users!"))
            return

        self.stdout.write('Seeding 5 long trips...')
        
        for i in range(5):
            ride = Ride.objects.create(
                status='dropoff',
                id_rider=rider,
                id_driver=driver,
                pickup_latitude=37.77, pickup_longitude=-122.41,
                dropoff_latitude=37.78, dropoff_longitude=-122.42,
                pickup_time=timezone.now()
            )
            
            # Base time: 2 days ago
            base_time = timezone.now() - timedelta(days=2)
            
            # Pickup Event
            # Note: RideEvent.created_at has auto_now_add=True, so we must
            # update the field AFTER creation to set custom timestamps.
            pickup_event = RideEvent.objects.create(
                id_ride=ride,
                description='Status changes to pickup',
            )
            pickup_event.created_at = base_time
            pickup_event.save(update_fields=['created_at'])
            
            # Dropoff Event: 3 HOURS later (Satisfies > 1h criteria)
            dropoff_event = RideEvent.objects.create(
                id_ride=ride,
                description='Status change to dropoff',
            )
            dropoff_event.created_at = base_time + timedelta(hours=3)
            dropoff_event.save(update_fields=['created_at'])
            
        self.stdout.write(self.style.SUCCESS('Seeded 5 long trips!'))