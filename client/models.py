from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room

# Create your models here.
class RoomServiceRequest(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('room cleaning', 'Room Cleaning'),
        ('change sheets', 'Change sheets'),
        ('washroom cleaning', 'Clean washroom'),
        ('waterbottles', 'Water Bottles'),
        ('toileteries', 'Toileteries'),
        ('cutlery', 'Cutlery'),
        ('electrical repair', 'Electrical Repairs'),
        ('plumbing repair', 'Plumbing Repairs'),
        ('room service', 'Request attendant'),
        ('SOS', 'SOS'),
        ('checkout', 'Checkout'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    is_serviced = models.BooleanField(default=False)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_requests")
    created_at = models.DateTimeField(auto_now_add=True)

class ServiceAvailability(models.Model):
    SERVICE_CHOICES = (
        ('room_service', 'Room Service'),
        ('laundry', 'Laundry'),
        ('cleaning', 'Cleaning'),
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, unique=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_service_type_display()}: {'Available' if self.is_available else 'Unavailable'}"  

    
      
