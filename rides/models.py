from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with role field.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('rider', 'Rider'),
        ('driver', 'Driver'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='rider')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = 'user'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Ride(models.Model):
    """
    Ride model - represents a single ride/trip.
    """
    STATUS_CHOICES = [
        ('en-route', 'En Route'),
        ('pickup', 'Pickup'),
        ('dropoff', 'Dropoff'),
    ]
    
    # In Django, we define the column name explicitly with db_column
    # ForeignKey is like belongsTo() in Laravel
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # related_name is like defining the inverse relationship name
    # This is how you'll access rides FROM a user: user.rides_as_rider.all()
    id_rider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_rider',
        db_column='id_rider'
    )
    id_driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_driver',
        db_column='id_driver'
    )
    
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()
    
    class Meta:
        db_table = 'ride'
        ordering = ['-pickup_time']  # Default ordering, like Laravel's $orderBy
    
    def __str__(self):
        return f"Ride {self.pk}: {self.id_rider} -> {self.status}"