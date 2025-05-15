from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from rooms.models import Room




class Facility(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="facilities")
    
    def __str__(self):
        return self.name
    
    def available_slots(self):
        """Return all available time slots for this facility"""
        return self.timeslot_set.filter(booking__isnull=True)

class TimeSlot(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.facility.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')} to {self.end_time.strftime('%H:%M')}"
    
    class Meta:
        ordering = ['start_time']
    
    

class Booking(models.Model):
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    settled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.time_slot}"