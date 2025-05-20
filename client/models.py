from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room
from core.models import ServiceType

# Create your models here.


class RoomServiceRequest(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    is_serviced = models.BooleanField(default=False)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    room_settled = models.BooleanField(default=False)






    
      
