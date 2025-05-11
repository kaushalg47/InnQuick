from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import json
from django.views.decorators.csrf import csrf_exempt
from .models import MenuItem, Order, OrderItem, User, Category
from rooms.models import Room
from django.contrib.auth.decorators import login_required
from datetime import time

@csrf_exempt
@login_required
def menu_list(request):
  items = MenuItem.objects.filter(user=request.user)
  categories = Category.objects.all()
  print([category.name for category in categories])
  print([items.name for items in items])

  category_items = {}
  for category in categories:
      category_items[category] = items.filter(category=category)

  context = {
      'category_items': category_items,
      'categories': categories,
      'items': items,  # for other uses
  }

  return render(request, 'addMenuItems.html', context)

@csrf_exempt
def place_order(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    items = data.get('items', [])
    print(items, data)
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    user = get_object_or_404(User, id=user_id)
    if not room_id:
      return JsonResponse({"error": "Room ID is required."}, status=400)
    room = Room.objects.get(id=room_id, user=user)
    
    order = Order.objects.create(user=user, room_id=room_id)
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
        price = data.get('price')
        description = data.get('description')
        category_id = data.get('category')

        if not name:
            return JsonResponse({"error": "Name is required."}, status=400)

        # Optional: Check if category exists
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return JsonResponse({"error": "Category not found."}, status=404)

        item = MenuItem.objects.create(
            name=name,
            user=request.user,
            price=price,
            description=description,
            category=category  # Assumes FK to Category in your model
        )

        return JsonResponse({
            "message": f"Menu item added successfully.",
            "item": {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "description": item.description,
                "category": item.category.id if item.category else None
            }
        }, status=201)

    return JsonResponse({"error": "Invalid request."}, status=400)


@csrf_exempt
@login_required
@require_POST
def toggle_active(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.is_active = not item.is_active
    item.save()
    return JsonResponse({'success': True, 'active': item.is_active})

@csrf_exempt
@login_required
@require_POST
def update_discount(request, item_id):
    data = json.loads(request.body)
    discount = data.get('discount')
    item = get_object_or_404(MenuItem, id=item_id)
    item.discount = discount
    item.save()
    return JsonResponse({'success': True, 'discount': item.discount})

@csrf_exempt
@login_required
@require_POST
def toggle_category_active(request, category_id):
    """
    Toggle active status for all menu items in a specified category
    """
    category = get_object_or_404(Category, id=category_id)
    
    # Check if user has permission to modify this category
    if category.created_by != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    # Get the new status - either from request or toggle all items to same value
    data = json.loads(request.body)
    new_status = data.get('active_status')
    
    # If no status provided, toggle all to the opposite of majority
    if new_status is None:
        # Determine the current majority status
        items = MenuItem.objects.filter(category=category, user=request.user)
        active_count = items.filter(is_active=True).count()
        inactive_count = items.filter(is_active=False).count()
        
        # Set new status to opposite of majority
        new_status = active_count <= inactive_count
    
    # Update all items in category
    updated_count = MenuItem.objects.filter(
        category=category, 
        user=request.user
    ).update(is_active=new_status)
    
    return JsonResponse({
        'success': True, 
        'category': category.name,
        'new_status': new_status,
        'updated_count': updated_count
    })


@csrf_exempt
@login_required
@require_POST
def update_category_discount(request, category_id):
    """
    Apply the same discount to all menu items in a specified category
    """
    category = get_object_or_404(Category, id=category_id)
    
    # Check if user has permission to modify this category
    if category.created_by != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    data = json.loads(request.body)
    discount = data.get('discount')
    
    # Validate discount value
    try:
        discount = float(discount)
        if discount < 0 or discount > 100:
            return JsonResponse({
                'success': False, 
                'error': 'Discount must be between 0 and 100'
            }, status=400)
    except (TypeError, ValueError):
        return JsonResponse({
            'success': False, 
            'error': 'Invalid discount value'
        }, status=400)
    
    # Update all items in category
    updated_count = MenuItem.objects.filter(
        category=category, 
        user=request.user
    ).update(discount=discount)
    
    return JsonResponse({
        'success': True, 
        'category': category.name,
        'discount': discount,
        'updated_count': updated_count
    })


@csrf_exempt
def create_category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        start_time = data.get('start_time')  # Expecting format: "HH:MM"
        end_time = data.get('end_time')

        user = request.user

        if not name:
            return JsonResponse({'success': False, 'error': 'Name is required'})

        if Category.objects.filter(name=name, created_by=user).exists():
            return JsonResponse({'success': False, 'error': 'Category already exists'})

        try:
            start = time.fromisoformat(start_time) if start_time else None
            end = time.fromisoformat(end_time) if end_time else None
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid time format'})

        category = Category.objects.create(
            name=name,
            created_by=user,
            start_time=start,
            end_time=end
        )

        return JsonResponse({
            'success': True,
            'category_id': category.id,
            'category_name': category.name
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)



@login_required
def delete_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id, user=request.user)
        item.delete()
        return JsonResponse({'message': 'Item deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

