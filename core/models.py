from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    
    tax_percentage = models.FloatField(default=0.0, help_text="Global tax percentage for the user.")
    additional_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.0, help_text="Any additional service charge.")

    is_menu_available = models.BooleanField(default=True, help_text="Toggle to show/hide the menu.")
    is_service_available = models.BooleanField(default=True, help_text="Toggle to enable/disable room service.")

    def __str__(self):
        return f"{self.user.username}'s Settings"
    
class ServiceType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_types")
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Price can be optional
    active = models.BooleanField(default=True)  # Toggle for service availability

    class Meta:
        unique_together = ('user', 'name')  # Prevent duplicate names per user

    def __str__(self):
        return f"{self.name} - ₹{self.price}"    

        
