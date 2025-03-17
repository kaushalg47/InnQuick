from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import MenuItem, Order, OrderItem
from rooms.models import Room
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def menu_list(request):
  items = MenuItem.objects.filter(user=request.user)
  return render(request, 'addMenuItems.html', {'items': items})

@csrf_exempt
@login_required
def place_order(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    items = data.get('items', [])
    print(items, data)
    room_id = data.get('room_id')
    if not room_id:
      return JsonResponse({"error": "Room ID is required."}, status=400)
    room = Room.objects.get(id=room_id, user=request.user)
    
    order = Order.objects.create(user=request.user, room_id=room_id)
    for item in items:
      menu_item = get_object_or_404(MenuItem, id=item['id'])
      OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item['quantity'])
    return JsonResponse({"message": "Order placed successfully."})
  return JsonResponse({"error": "Invalid request."}, status=400)

@login_required
def order_list(request):
  orders = Order.objects.filter(user=request.user,status="Pending").prefetch_related('orderitem_set__menu_item')
  order_data = []
  for order in orders:
    items = []
    for order_item in order.orderitem_set.all():
      items.append({
        'name': order_item.menu_item.name,
        'quantity': order_item.quantity,
        'price': order_item.menu_item.price
      })
    order_data.append({
      'id': order.id,
      'room': order.room.number,
      'status': order.status,
      'created_at': order.created_at,
      'items': items
    })
  return render(request, 'ManageOrders.html', {'orders': order_data})

def completed_orders(request):
  orders = Order.objects.filter(user=request.user, status="Completed").prefetch_related('orderitem_set__menu_item')
  order_data = []
  for order in orders:
    items = []
    total_price = 0
    for order_item in order.orderitem_set.all():
      item_price = order_item.menu_item.price * order_item.quantity
      total_price += item_price
      items.append({
        'name': order_item.menu_item.name,
        'quantity': order_item.quantity,
        'price': order_item.menu_item.price,
        'total_item_price': item_price
      })
    order_data.append({
      'id': order.id,
      'status': order.status,
      'created_at': order.created_at,
      'items': items,
      'total_price': total_price
    })
  return render(request, 'AllOrders.html', {'orders': order_data})



@login_required
def mark_order_done(request, order_id):
  order = get_object_or_404(Order, id=order_id)
  order.status = 'Completed'
  order.save()
  print(order.status)
  return JsonResponse({"message": "Request marked as serviced."})

@csrf_exempt
@login_required
def add_menu_item(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    name = data.get('name')
    if not name:
      return JsonResponse({"error": "Name is required."}, status=400)
    
    item = MenuItem.objects.create(name=name, user=request.user, price=data.get('price'), description=data.get('description'))
    return JsonResponse({
      "message": "Menu item added successfully.{item.description}",
      "item":{
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "description": item.description
      }
      }, status=201)
  return JsonResponse({"error": "Invalid request."}, status=400)

@login_required
def delete_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id, user=request.user)
        item.delete()
        return JsonResponse({'message': 'Item deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

