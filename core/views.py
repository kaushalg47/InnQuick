from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserSettings, ServiceType
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from client.models import RoomServiceRequest
from menu.models import Order
from facility.models import Booking



@login_required
def user_settings_view(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    services = ServiceType.objects.filter(user=request.user)
    return render(request, 'settings.html', {
        'settings': settings,
        'services': services
    })


@login_required
def update_settings(request):
    if request.method == 'POST':
        settings = request.user.settings
        settings.tax_percentage = request.POST.get('tax_percentage') or 0.0
        settings.additional_charge = request.POST.get('additional_charge') or 0.0
        settings.is_menu_available = 'is_menu_available' in request.POST
        settings.is_service_available = 'is_service_available' in request.POST
        settings.save()
        return redirect('user_settings_view')
    

@login_required
def service_type_list(request):
    services = ServiceType.objects.filter(user=request.user)
    return render(request, 'core/service_types.html', {'services': services})

@csrf_exempt
@login_required
def add_service_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')

        if not name:
            return JsonResponse({'error': 'Name is required.'}, status=400)

        final_price = None  # Default if price is not provided

        if price:
            try:
                final_price = Decimal(price)
            except InvalidOperation:
                return JsonResponse({'error': 'Invalid price format.'}, status=400)

        service, created = ServiceType.objects.get_or_create(
            user=request.user,
            name=name.strip().lower(),
            defaults={'price': final_price}
        )

        if not created:
            return JsonResponse({'error': 'Service already exists.'}, status=409)

        return JsonResponse({
            "message": "Service added successfully.",
            "item": {
                "id": service.id,
                "name": service.name,
                "price": float(service.price) if service.price is not None else None
            }
        }, status=201)

    return JsonResponse({'error': 'Only POST method allowed.'}, status=405)


@csrf_exempt
@login_required
def delete_service_type(request, service_id):
    if request.method == 'POST':
        service = get_object_or_404(ServiceType, id=service_id, user=request.user)
        service.delete()
    return JsonResponse({
            "message": f"Deleted successfully.",
        }, status=201)


import logging
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def get_all_data(request):
    try:
        # Get the data from the database
        service_requests = RoomServiceRequest.objects.filter(user=request.user)
        food_orders = Order.objects.filter(user=request.user)
        facility_bookings = Booking.objects.filter(user=request.user)
        
        # Process service requests with error handling
        service_requests_data = []
        for sr in service_requests:
            try:
                service_requests_data.append({
                    'id': sr.id,
                    'room': sr.room.number if hasattr(sr, 'room') and sr.room else 'N/A',
                    'service_type': sr.service_type.name if hasattr(sr, 'service_type') and sr.service_type else 'N/A',
                    'is_serviced': sr.is_serviced if hasattr(sr, 'is_serviced') else False,
                    'created_at': sr.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(sr, 'created_at') and sr.created_at else 'N/A',
                    'room_settled': sr.room_settled if hasattr(sr, 'room_settled') else False
                })
            except Exception as e:
                logger.error(f"Error processing service request {sr.id}: {str(e)}")
                # Continue processing other items
        
        # Process food orders with error handling
        food_orders_data = []
        for order in food_orders:
            try:
                room_number = None
                if hasattr(order, 'room') and order.room:
                    if hasattr(order.room, 'room_number'):
                        room_number = order.room.room_number
                    elif hasattr(order.room, 'number'):
                        room_number = order.room.number
                
                food_orders_data.append({
                    'id': order.id,
                    'room': room_number,
                    'status': order.status if hasattr(order, 'status') else 'unknown',
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(order, 'created_at') and order.created_at else 'N/A',
                    'settled': order.settled if hasattr(order, 'settled') else False,
                    'room_settled': order.room_settled if hasattr(order, 'room_settled') else False
                })
            except Exception as e:
                logger.error(f"Error processing food order {order.id}: {str(e)}")
                # Continue processing other items
        
        # Process facility bookings with error handling
        facility_bookings_data = []
        for booking in facility_bookings:
            try:
                # Check if booking has all required attributes
                facility_name = 'N/A'
                start_time = 'N/A'
                end_time = 'N/A'
                
                if hasattr(booking, 'time_slot') and booking.time_slot:
                    if hasattr(booking.time_slot, 'facility') and booking.time_slot.facility:
                        facility_name = booking.time_slot.facility.name
                    
                    if hasattr(booking.time_slot, 'start_time') and booking.time_slot.start_time:
                        start_time = booking.time_slot.start_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if hasattr(booking.time_slot, 'end_time') and booking.time_slot.end_time:
                        end_time = booking.time_slot.end_time.strftime('%Y-%m-%d %H:%M:%S')
                
                facility_bookings_data.append({
                    'id': booking.id,
                    'facility': facility_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'settled': booking.settled if hasattr(booking, 'settled') else False
                })
            except Exception as e:
                logger.error(f"Error processing facility booking {booking.id}: {str(e)}")
                # Continue processing other items
        
        # Combine all data and return as JSON response
        data = {
            'service_requests': service_requests_data,
            'food_orders': food_orders_data,
            'facility_bookings': facility_bookings_data
        }
        
        return JsonResponse(data, safe=True)
        
    except Exception as e:
        # Log the full exception with traceback
        logger.error(f"Error in get_all_data: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@login_required
def admin_dashboard(request):
        # Handle the GET request here
        return render(request, 'AdminDashboard.html')    