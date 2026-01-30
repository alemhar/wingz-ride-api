from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.utils import timezone
from django.db.models import Prefetch, F, ExpressionWrapper, FloatField
from django.db.models.functions import Power, Sqrt
from datetime import timedelta
from math import radians, cos

from .models import User, Ride, RideEvent
from .serializers import (
    UserSerializer, 
    RideSerializer, 
    RideCreateUpdateSerializer,
    RideEventSerializer
)
from .permissions import IsAdminRole

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import connection

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    
    Laravel equivalent: UserController with index, show, store, update, destroy.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


class RideFilter(filters.FilterSet):
    """
    FilterSet for Ride - like Laravel's query scopes or Spatie Query Builder.
    """
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    rider_email = filters.CharFilter(field_name='id_rider__email', lookup_expr='icontains')
    
    class Meta:
        model = Ride
        fields = ['status', 'rider_email']


class RideViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ride CRUD with optimized queries.
    
    Key performance features:
    1. Uses select_related for FK relationships (rider, driver) - 1 JOIN query
    2. Uses Prefetch for RideEvents with filtered queryset - 1 additional query
    3. Total: 2 queries (+ 1 for pagination count)
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_class = RideFilter
    ordering_fields = ['pickup_time']
    ordering = ['-pickup_time']
    
    def get_queryset(self):
        """
        Build optimized queryset with eager loading.
        
        Laravel equivalent:
        Ride::with(['rider', 'driver'])
            ->with(['rideEvents' => fn($q) => $q->where('created_at', '>=', now()->subDay())])
        """
        # Calculate 24 hours ago
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        # Prefetch only today's ride events (performance requirement)
        todays_events_prefetch = Prefetch(
            'ride_events',
            queryset=RideEvent.objects.filter(created_at__gte=twenty_four_hours_ago),
            to_attr='todays_events'  # This creates a new attribute on the Ride object
        )
        
        queryset = Ride.objects.select_related(
            'id_rider',  # Like with('rider') - JOINs the user table
            'id_driver'  # Like with('driver') - JOINs same user table
        ).prefetch_related(
            todays_events_prefetch  # Separate query for events
        )
        
        # Handle distance-based sorting if lat/lng provided
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        sort_by = self.request.query_params.get('sort_by')
        
        if lat and lng and sort_by == 'distance':
            lat = float(lat)
            lng = float(lng)
            
            # Haversine-like distance calculation in database
            # This calculates approximate distance using Euclidean formula
            # Good enough for sorting purposes
            lat_diff = F('pickup_latitude') - lat
            lng_diff = F('pickup_longitude') - lng
            
            # Simplified distance formula (works for sorting)
            distance = ExpressionWrapper(
                Sqrt(Power(lat_diff, 2) + Power(lng_diff, 2)),
                output_field=FloatField()
            )
            
            queryset = queryset.annotate(distance=distance).order_by('distance')
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for read vs write operations.
        
        Laravel equivalent: Different Resources for different actions.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return RideCreateUpdateSerializer
        return RideSerializer


class RideEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RideEvent CRUD operations.
    """
    queryset = RideEvent.objects.select_related('id_ride')
    serializer_class = RideEventSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def trip_duration_report(request):
    """
    Raw SQL report: Trips taking more than 1 hour, grouped by Month and Driver.
    """

    # sql = """
    # SELECT 
    #     pickup_event.created_at as raw_pickup,
    #     dropoff_event.created_at as raw_dropoff,
    #     julianday(pickup_event.created_at) as julian_pickup,
    #     julianday(dropoff_event.created_at) as julian_dropoff
    # FROM ride r
    # JOIN ride_event pickup_event ON pickup_event.id_ride = r.id AND pickup_event.description = 'Status changes to pickup'
    # JOIN ride_event dropoff_event ON dropoff_event.id_ride = r.id AND dropoff_event.description = 'Status change to dropoff'
    # -- No WHERE, No GROUP BY
    # LIMIT 5
    # """

    sql = """
    SELECT 
        strftime('%Y-%m', pickup_event.created_at) as month,
        u.first_name || ' ' || u.last_name as driver,
        COUNT(*) as trip_count
    FROM ride r
    JOIN user u ON r.id_driver = u.id
    JOIN ride_event pickup_event ON pickup_event.id_ride = r.id 
        AND pickup_event.description = 'Status changes to pickup'
    JOIN ride_event dropoff_event ON dropoff_event.id_ride = r.id 
        AND dropoff_event.description = 'Status change to dropoff'
    WHERE (julianday(dropoff_event.created_at) - julianday(pickup_event.created_at)) * 24 > 1
    GROUP BY month, driver
    ORDER BY month, driver
    """   
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return Response({
        'report': 'Trips > 1 Hour by Month and Driver',
        'data': rows
    })