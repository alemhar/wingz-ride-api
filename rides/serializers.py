from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import User, Ride, RideEvent


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'phone_number']
        read_only_fields = ['id']


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = ['id', 'id_ride', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class RideSerializer(serializers.ModelSerializer):
    # Nested serializers (like Laravel's whenLoaded())
    id_rider = UserSerializer(read_only=True)
    id_driver = UserSerializer(read_only=True)
    
    # This will be populated with only today's events (performance requirement)
    todays_ride_events = RideEventSerializer(many=True, read_only=True, source='todays_events')
    
    class Meta:
        model = Ride
        fields = [
            'id', 'status', 'id_rider', 'id_driver',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'pickup_time', 'todays_ride_events'
        ]


class RideCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Separate serializer for creating/updating rides.
    Uses IDs instead of nested objects for input.
    
    """
    id_rider = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    id_driver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Ride
        fields = [
            'id', 'status', 'id_rider', 'id_driver',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'pickup_time'
        ]