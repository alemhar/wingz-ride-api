from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with role field.
    
    Laravel equivalent: User model in app/Models/User.php
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('rider', 'Rider'),
        ('driver', 'Driver'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='rider')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = 'user'  # Explicit table name like Laravel's $table
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"