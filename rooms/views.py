import base64
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Room
from client.models import RoomServiceRequest
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import qrcode
import os
import time
from django.http import JsonResponse
from django.shortcuts import render

# Admin login view
def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('get_room_service_requests')  # Redirect to admin dashboard or home
    else:
        form = AuthenticationForm()

    return render(request, 'AdminLogin.html', {'form': form}) 

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def admin_dashboard(request):
    return render(request, 'AdminDashboard.html')

@login_required
def fetch_rooms(request):
    rooms = Room.objects.filter(user=request.user)
    for room in rooms:
        room.qr_code_url = f"{settings.MEDIA_URL}{room.qr_code}" if room.qr_code else None

    # Pass rooms and their qr_code_url to the template
    return render(request, 'ViewRooms.html', {'rooms': rooms})

def client_dashboard(request):
    return render(request, 'UserHome.html')


@csrf_exempt
def request_room_service(request, room_id):
    if request.method == 'POST':
        room = Room.objects.get(id=room_id, user=request.user)
        RoomServiceRequest.objects.create(room=room, user=request.user)
        return JsonResponse({"message": "Room service requested successfully."})

@login_required
def add_room(request):
    if request.method == 'POST':
        data = json.loads(request.body)  
        room_number = data.get('number')
        if not room_number:
            return JsonResponse({'error': 'Room number is required'}, status=400)
        if Room.objects.filter(number=room_number, user=request.user).exists():
            return JsonResponse({'error': 'Room number already exists'}, status=400)
        
        room = Room.objects.create(number=room_number,user=request.user)
        room_url = f"{settings.BASE_URL}/client/{room.id}/{request.user.id}"
        room.url = room_url
        room.save()

        qr_image = qrcode.make(room_url)
        qr_image_path = f'qr_codes/{room.id}-{room.number}.png'
        full_path = os.path.join(settings.MEDIA_ROOT, qr_image_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        qr_image.save(full_path)

        room.qr_code = qr_image_path
        room.save()

        return JsonResponse({
            'message': 'Room created successfully',
            'room': {
                'id': room.id,
                'number': room.number,
                'url': room.url,
            },
            'qr_code_url': f"{settings.MEDIA_URL}{qr_image_path}"
        }, status=201)



# @login_required
# def get_rooms(request):
#     if request.method == 'GET':
#         rooms = Room.objects.filter(user=request.user)
#         serializer = RoomSerializer(rooms, many=True)
#         return JsonResponse(serializer.data, safe=False, status=200)
    


@login_required
def delete_room(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id, user=request.user)
        if room.qr_code:
            qr_code_path = os.path.join(settings.MEDIA_ROOT, str(room.qr_code))
            if os.path.isfile(qr_code_path):
                os.remove(qr_code_path)
        room.delete()
        return JsonResponse({'message': 'Room deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@login_required
def get_room_service_requests(request):
    if request.method == 'GET':
        requests = RoomServiceRequest.objects.filter(user=request.user, is_serviced=False)

        # Handle AJAX requests by returning JSON data
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'requests': [
                    {
                        'id': req.id,
                        'room': {'number': req.room.number},
                        'service_type': req.service_type,
                        'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for req in requests
                ]
            })

        # Otherwise, render the normal page
        return render(request, 'ViewRequests.html', {'requests': requests})

@csrf_exempt
@login_required
def mark_as_serviced(request, request_id):
    if request.method == 'POST':
        room_service_request = RoomServiceRequest.objects.get(id=request_id, user=request.user)
        room_service_request.is_serviced = True
        room_service_request.save()
        return JsonResponse({"message": "Request marked as serviced."})
    
def generate_qr_code(url):
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()  



# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import Room
from client.models import RoomServiceRequest
from menu.models import Order, OrderItem
from django.db.models import Sum, F
from decimal import Decimal

def room_dashboard(request):
    """
    Render the room dashboard template with all available rooms
    """
    rooms = Room.objects.filter(user=request.user).order_by('number')
    return render(request, 'RoomDashboard.html', {
        'rooms': rooms
    })

def room_data_api(request, room_id):
    """
    API endpoint to get all service requests and food orders for a specific room
    """
    try:
        # Fetch the room
        room = Room.objects.get(id=room_id, user=request.user)
        
        # Get all service requests for this room
        service_requests = RoomServiceRequest.objects.filter(
            room=room, room_settled=False
        ).select_related('service_type').order_by('-created_at')
        
        # Get all food orders for this room
        orders = Order.objects.filter(
            room=room, room_settled=False
        ).prefetch_related('orderitem_set__menu_item').order_by('-created_at')
        
        # Calculate service requests total
        services_total = Decimal('0.00')
        food_total = Decimal('0.00')
        
        for service in service_requests:
            if service.service_type.price:
                if isinstance(service.service_type.price, float):
                    services_total += Decimal(str(service.service_type.price))
                else:
                    services_total += service.service_type.price
        
        # Prepare service request data
        service_requests_data = []
        for service in service_requests:
            service_requests_data.append({
                'id': service.id,
                'is_serviced': service.is_serviced,
                'created_at': service.created_at.isoformat(),
                'service_type': {
                    'name': service.service_type.name,
                    'price': float(service.service_type.price) if service.service_type.price else 0.00
                }
            })
        
        # Prepare food order data
        food_orders_data = []
        
        
        for order in orders:
            order_items = []
            for order_item in order.orderitem_set.all():
                menu_item = order_item.menu_item
                price = menu_item.discounted_price if menu_item.discounted_price is not None else menu_item.price
                
                order_items.append({
                    'name': menu_item.name,
                    'quantity': order_item.quantity,
                    'price': float(price),
                    'discounted_price': float(menu_item.discounted_price) if menu_item.discounted_price else None,
                    'subtotal': float(order_item.subtotal)
                })
            
            # Add order total to the running total
            
            food_total = Decimal('0.00')
            for order in orders:
                # ... code for order items ...
                if isinstance(order.total_price, float):
                    food_total += Decimal(str(order.total_price))
                else:
                    food_total += order.total_price
            
            food_orders_data.append({
                'id': order.id,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'items': order_items,
                'total_price': float(order.total_price)
            })
        
        # Prepare response
        data = {
            'room_id': room.id,
            'room_number': room.number,
            'service_requests': service_requests_data,
            'food_orders': food_orders_data,
            'services_total': float(services_total),
            'food_total': float(food_total),
            'grand_total': float(services_total + food_total)
        }
        
        return JsonResponse(data)
    
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@login_required
def update_room_settled(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)

        # Get all service requests for this room
        service_requests = RoomServiceRequest.objects.filter(
            room=room, room_settled=False
        ).select_related('service_type').order_by('-created_at')
        
        # Get all food orders for this room
        orders = Order.objects.filter(
            room=room, room_settled=False
        ).prefetch_related('orderitem_set__menu_item').order_by('-created_at')

        # Update each service request individually
        for service_request in service_requests:
            service_request.room_settled = True
            service_request.save()

        # Update each order individually
        for order in orders:
            order.room_settled = True
            order.save()
        
        # For AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        # For regular form submissions, redirect back to a page
        return redirect('room_detail', room_id=room_id)
    
    # If not a POST request, redirect to room detail
    return redirect('room_detail', room_id=room_id)


