from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Ride


class RideAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password',
            role='admin'
        )
        self.client.force_authenticate(user=self.admin)
    
    def test_ride_list_requires_auth(self):
        self.client.logout()
        response = self.client.get('/api/rides/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_ride_list_requires_admin_role(self):
        rider = User.objects.create_user(
            username='rider',
            email='rider@test.com',
            password='password',
            role='rider'
        )
        self.client.force_authenticate(user=rider)
        response = self.client.get('/api/rides/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_list_rides(self):
        response = self.client.get('/api/rides/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_trip_duration_report(self):
        """
        Verify the raw SQL report works correctly with controlled data.
        """
        from datetime import timedelta
        from django.utils import timezone
        from .models import RideEvent
        
        # 1. Create a Driver
        driver = User.objects.create_user(
            username='driver1',
            email='driver1@test.com',
            password='password',
            first_name='Test',
            last_name='Driver',
            role='driver'
        )
        
        # 2. Create a Ride
        ride = Ride.objects.create(
            status='dropoff',
            id_rider=self.admin, # Reuse admin as rider for simplicity
            id_driver=driver,
            pickup_latitude=0, pickup_longitude=0,
            dropoff_latitude=0, dropoff_longitude=0,
            pickup_time=timezone.now()
        )
        
        # 3. Create Events (Duration = 25 hours)
        # Note: RideEvent.created_at has auto_now_add=True, so we must
        # update the field AFTER creation to set custom timestamps.
        base_time = timezone.now() - timedelta(days=1)
        
        pickup_event = RideEvent.objects.create(
            id_ride=ride,
            description='Status changes to pickup',
        )
        pickup_event.created_at = base_time
        pickup_event.save(update_fields=['created_at'])
        
        dropoff_event = RideEvent.objects.create(
            id_ride=ride,
            description='Status change to dropoff',
        )
        dropoff_event.created_at = base_time + timedelta(hours=25)
        dropoff_event.save(update_fields=['created_at'])
        
        # 4. Call the Report Endpoint
        response = self.client.get('/api/reports/trip-duration/')
        
        # 5. Verify Results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report_data = response.json()['data']
        
        self.assertEqual(len(report_data), 1)
        self.assertEqual(report_data[0]['driver'], 'Test Driver')
        self.assertEqual(report_data[0]['trip_count'], 1)
