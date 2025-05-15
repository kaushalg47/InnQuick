from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class MenuItem(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="menu")
  name = models.CharField(max_length=100)
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
  description = models.TextField(max_length=300)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  is_active = models.BooleanField(default=True)  # Toggle
  discount = models.FloatField(default=0.0) 
  discounted_price = models.FloatField(blank=True, null=True)

  
  
  def __str__(self):
    return self.name
  


class Table(models.Model):
  table_number = models.CharField(max_length=10, unique=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tables")
  is_available = models.BooleanField(default=True)
  empty = models.BooleanField(default=True)

  def __str__(self):
    return self.table_number   

class Order(models.Model):
  STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
  ]
  items = models.ManyToManyField(MenuItem, through='OrderItem')
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
  created_at = models.DateTimeField(auto_now_add=True)
  room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
  table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
  settled = models.BooleanField(default=False)

  def __str__(self):
    return f"Order {self.id} - {self.status}"
  
  @property
  def total_price(self):
      total = Decimal('0.00')  # Start with a Decimal instead of integer 0
      for order_item in self.orderitem_set.all():
          menu_item = order_item.menu_item
          price = menu_item.discounted_price if menu_item.discounted_price is not None else menu_item.price
          
          # Convert price to Decimal if it's not already
          if not isinstance(price, Decimal):
              price = Decimal(str(price))
              
          # Convert quantity to Decimal for the calculation
          quantity = Decimal(str(order_item.quantity))
          
          total += price * quantity
      return total


class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField()

  def __str__(self):
    return f"{self.quantity} x {self.menu_item.name} for Order {self.order.id}"
  
  @property
  def subtotal(self):
      price = self.menu_item.discounted_price if self.menu_item.discounted_price is not None else self.menu_item.price
      return price * self.quantity
  

  # tables



    


