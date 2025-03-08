from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room

class MenuItem(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="menu")
  name = models.CharField(max_length=100)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  
  def __str__(self):
    return self.name
  

class Order(models.Model):
  STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
  ]
  items = models.ManyToManyField(MenuItem, through='OrderItem')
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
  created_at = models.DateTimeField(auto_now_add=True)
  room = models.ForeignKey(Room, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

  def __str__(self):
    return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField()

  def __str__(self):
    return f"{self.quantity} x {self.menu_item.name} for Order {self.order.id}"
