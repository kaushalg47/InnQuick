from django.contrib import admin
from .models import MenuItem, Order, OrderItem  # Import your models here

# Register your models here
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
