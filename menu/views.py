from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import json
from django.views.decorators.csrf import csrf_exempt
from .models import MenuItem, Order, OrderItem, User, Category, Table
from django.contrib import messages
from rooms.models import Room
from django.contrib.auth.decorators import login_required
from datetime import time
from decimal import Decimal


@csrf_exempt
@login_required
def menu_list(request):
  items = MenuItem.objects.filter(user=request.user)
  categories = Category.objects.all()
  print([category.name for category in categories])
  print([items.discounted_price for items in items])

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

    location_info = None
    location_label = None
    
    if order.room:
        location_info = order.room.number
        location_label = "Room"
    elif order.table:
        location_info = order.table.table_number
        location_label = "Table"
    else:
        location_info = "Unknown"
        location_label = "Location"
    
    order_data.append({
        'id': order.id,
        'location_info': location_info,
        'location_label': location_label,
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

    try:
        # Safely convert discount to float
        discount = float(str(discount).strip())
        item.discount = discount
        # Calculate discounted price
        if item.price is not None:
            item.discounted_price = float(item.price) - (float(item.price) * discount / 100)
        item.save()
        return JsonResponse({
            'success': True,
            'discount': item.discount,
            'price': float(item.price),  # ✅ Add this line
            'discounted_price': item.discounted_price
        })
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid discount value'}, status=400)




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
@login_required
@require_POST
def delete_category(request, category_id):
    """
    Delete an entire category and all its associated menu items
    """
    category = get_object_or_404(Category, id=category_id)
    
    # Check if user has permission to delete this category
    if category.created_by != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    # Count items to be deleted for the response message
    item_count = MenuItem.objects.filter(category=category, user=request.user).count()
    category_name = category.name
    
    try:
        # Delete all menu items in this category first
        MenuItem.objects.filter(category=category, user=request.user).delete()
        
        # Then delete the category itself
        category.delete()
        
        return JsonResponse({
            'success': True,
            'message': f"Category '{category_name}' and {item_count} menu items deleted successfully."
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)



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




@login_required
def table_list(request):
    """Render the manage table page and list all tables."""
    tables = Table.objects.filter(user=request.user).order_by('table_number')
    return render(request, 'ManageTable.html', {'tables': tables})




@login_required
def add_table(request):
    """Add a new table via form POST."""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, "Table number is required.")
            return redirect('table_list')
        
        table = Table.objects.create(user=request.user, table_number=name)
        messages.success(request, f"Table {table.table_number} has been added successfully.")
        return redirect('table_list')
    
    return JsonResponse({"error": "Only POST method allowed."}, status=405)


@login_required
def delete_table(request, pk):
    """Delete a table via POST request."""
    table = get_object_or_404(Table, pk=pk, user=request.user)
    
    if Order.objects.filter(table=table, status='Pending').exists():
        return JsonResponse({
            "error": f"Cannot delete table {table.table_number} as it has active orders."
        }, status=400)
    
    if request.method == 'POST':
        table_number = table.table_number
        table.delete()
        return JsonResponse({"success": True, "table_number": table_number})
    
    return JsonResponse({"error": "Only POST method allowed."}, status=405)



@login_required
def rpos_screen(request, table_id):
    """Render the RPOS screen for a specific table."""
    table = get_object_or_404(Table, id=table_id, user=request.user)
    menu_items = MenuItem.objects.filter(user=request.user)
    categories = Category.objects.all()
    orders = Order.objects.filter(table=table, settled=False).order_by('-created_at')

    # Map categories to their menu items
    category_items = {
        category: menu_items.filter(category=category)
        for category in categories
    }

    # Format orders
    order_data = []
    for order in orders:
        order_items = []
        for order_item in order.orderitem_set.all():
            order_items.append({
                'name': order_item.menu_item.name,
                'quantity': order_item.quantity,
                'price': order_item.menu_item.price
            })
        order_data.append({
            'id': order.id,
            'room': getattr(order.room, 'number', None),  # Safe check
            'status': order.status,
            'created_at': order.created_at,
            'items': order_items
        })

    context = {
        'category_items': category_items,
        'categories': categories,
        'items': menu_items,  # original list
        'table': table,
        'orders': order_data
    }

    return render(request, 'RposScreen.html', context)
    

@login_required
def rpos_place_order(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Only POST method is allowed."}, status=405)
    
    try:
        # Parse the JSON data from the request
        data = json.loads(request.body.decode('utf-8'))
        
        # Get table ID and validate
        table_id = data.get('table_id')
        if not table_id:
            return JsonResponse({"success": False, "error": "Table ID is required."}, status=400)
        
        # Get items and validate
        items = data.get('items', [])
        if not items:
            return JsonResponse({"success": False, "error": "No items provided."}, status=400)
        
        # Use the logged-in user directly from request
        user = request.user
        
        # Get the table and verify ownership
        try:
            table = Table.objects.get(id=table_id, user=user)
        except Table.DoesNotExist:
            return JsonResponse({"success": False, "error": "Table not found or access denied."}, status=404)
        
        # Create the order with just the user and table - room is optional in your model
        order = Order.objects.create(
            user=user,
            table=table,
            room=None,  # Set room to None since it's not required
            status='Pending'
        )
        
        # Process menu items
        order_items_created = 0
        for item in items:
            # Check for both possible field names
            menu_item_id = item.get('menu_item_id') or item.get('id')
            quantity = item.get('quantity')
            
            # Skip invalid items
            if not menu_item_id or not quantity or int(quantity) <= 0:
                continue
            
            try:
                menu_item = MenuItem.objects.get(id=menu_item_id, user=user)
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity
                )
                order_items_created += 1
            except MenuItem.DoesNotExist:
                # Log but don't fail the whole order
                print(f"Menu item {menu_item_id} not found or doesn't belong to user {user.id}")
                continue
        
        # If no valid items were added, delete the order and return error
        if order_items_created == 0:
            order.delete()
            return JsonResponse({"success": False, "error": "No valid items could be added to the order."}, status=400)
        
        if table.empty:
            table.empty = False
            table.save()  
        
        return JsonResponse({
            "success": True,
            "order_id": order.id,
            "message": "Order placed successfully."
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON data."}, status=400)
    except Exception as e:
        # Log the exception details
        import traceback
        print(f"Error processing order: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    


@login_required
@require_POST
def settle_all_table_orders(request, table_id):
    """
    View to settle all unsettled orders for a specific table.
    Updates all unsettled orders' settled status to True.
    """
    try:
        # Get the table (ensure it belongs to the current user)
        table = get_object_or_404(Table, id=table_id, user=request.user)
        
        # Get all unsettled orders for this table
        unsettled_orders = Order.objects.filter(table=table, settled=False)
        
        # Count the number of orders we're settling
        num_orders = unsettled_orders.count()
        
        if num_orders == 0:
            return JsonResponse({
                'success': False,
                'error': 'No unsettled orders found for this table'
            }, status=400)
        
        # Calculate the total amount being settled
        # Note: If your Order model has a 'total' field, use that.
        # Otherwise, calculate it from order items
        total_amount = 0
        for order in unsettled_orders:
            order_total = 0
            for order_item in order.orderitem_set.all():
                order_total += order_item.quantity * order_item.menu_item.price
            total_amount += order_total
        
        # Update all orders to settled=True
        unsettled_orders.update(settled=True)
        table.empty = True
        table.save()
        
        # Return success response with details
        return JsonResponse({
            'success': True,
            'message': f'Successfully settled {num_orders} orders',
            'orders_settled': num_orders,
            'total_amount': total_amount,
        })
        
    except Exception as e:
        # Return error response
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    


@login_required
@require_POST
def add_bill_to_table(request, table_id):
    """
    View to settle all unsettled orders for a specific table.
    Updates all unsettled orders' settled status to True.
    """
    try:
        # Get the table (ensure it belongs to the current user)
        room_number = request.POST.get('room_number')
        print(room_number)
        

        room = get_object_or_404(Room, number=room_number, user=request.user)

        table = get_object_or_404(Table, id=table_id, user=request.user)
        
        # Get all unsettled orders for this table
        unsettled_orders = Order.objects.filter(table=table, settled=False)
        
        # Count the number of orders we're settling
        num_orders = unsettled_orders.count()
        
        if num_orders == 0:
            return JsonResponse({
                'success': False,
                'error': 'No unsettled orders found for this table'
            }, status=400)
        
        # Calculate the total amount being settled
        # Note: If your Order model has a 'total' field, use that.
        # Otherwise, calculate it from order items
        total_amount = 0
        for order in unsettled_orders:
            order_total = 0
            for order_item in order.orderitem_set.all():
                order_total += order_item.quantity * order_item.menu_item.price
            total_amount += order_total
        
        # Update all orders to settled=True
        unsettled_orders.update(room=room, settled=True)

        table.empty = True
        table.save()
        
        # Return success response with details
        return JsonResponse({
            'success': True,
            'message': f'Successfully settled {num_orders} orders',
            'orders_settled': num_orders,
            'total_amount': total_amount,
        })
        
    except Exception as e:
        # Return error response
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)    
    

@login_required
def pos_table_list(request):
    """Render the manage table page and list all tables."""
    tables = Table.objects.filter(user=request.user).order_by('table_number')
    return render(request, 'Rpos.html', {'tables': tables})    

@login_required
def pos_orders(request):
    """Render the manage table page and list all tables."""
    orders = Order.objects.filter(user=request.user)
    return JsonResponse({
        'orders': [
            {
                'id': order.id,
                'room': getattr(order.room, 'number', None), 
                'table': getattr(order.room, 'number', None),  # Safe check
                'status': order.status,
                'created_at': order.created_at,
                'total_price': order.total_price
            } for order in orders
        ]
    }) 




    
   
