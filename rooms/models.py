from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import qrcode
from io import BytesIO
from django.core.files import File

class Room(models.Model):
    number = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    url = models.CharField(max_length=255, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # Store QR code image

    # def save(self, *args, **kwargs):
    #     if not self.qr_code:  # Only generate QR code if not already saved
    #         qr = qrcode.make(self.url)
    #         buffer = BytesIO()
    #         qr.save(buffer, format='PNG')
    #         self.qr_code.save(f'room_{self.id}_qr.png', File(buffer), save=False)
    #     super().save(*args, **kwargs)    

    def __str__(self):
        return self.number


admin.site.register(Room)    