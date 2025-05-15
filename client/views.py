import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required



# rooms/views.py
from .models import Room, RoomServiceRequest
from menu.models import MenuItem, Category
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
from core.models import ServiceType


# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Room, User, ServiceType, RoomServiceRequest

def room_service_interface(request, room_id, user_id):
    """
    Renders the user service interface showing all available service types
    """
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    available_services = ServiceType.objects.filter(user=request.user, active=True)
    
    return render(request, 'UserService.html', {
        'room': room, 
        'available_services': available_services, 
        'user': user
    })

# @csrf_exempt
# def request_room_service(request, room_id, user_id):
#     """
#     Handles the AJAX request when a user confirms a service request
#     """
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             service_type_name = data.get('service_type')
            
#             # Get the service type object
#             service_type = get_object_or_404(ServiceType, 
#                                            user=request.user, 
#                                            name=service_type_name,
#                                            active=True)
            
#             user = get_object_or_404(User, id=user_id)
#             room = get_object_or_404(Room, id=room_id)
            
#             # Create the service request
#             RoomServiceRequest.objects.create(
#                 room=room,
#                 user=user,
#                 service_type=service_type_name,
#                 price=service_type.price  # Store the price at time of request
#             )
            
#             return JsonResponse({"message": "Room service requested successfully."})
            
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
            
#     return JsonResponse({"error": "Only POST method is allowed."}, status=405)





def room_menu_interface(request, room_id, user_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    
    # Get all categories for this user
    categories = Category.objects.filter(created_by=user)
    
    # Get all active menu items for this user
    items = MenuItem.objects.filter(user=user)
    
    # Calculate discounted prices for items with discounts
    for item in items:
        if item.discount > 0:
            # Calculate discounted price if not already set
            if item.discounted_price is None:
                item.discounted_price = float(item.price) * (1 - (item.discount / 100))
                item.save()
    
    # Get current time to check category availability
    current_time = timezone.now().time()
    
    # Create a sorted list of categories with available ones first
    sorted_categories = []
    available_categories = []
    unavailable_categories = []
    
    for category in categories:
        if category.start_time and category.end_time:
            is_available = category.start_time <= current_time <= category.end_time
        else:
            is_available = True
            
        # Add availability flag to the category object
        category.is_available = is_available
        
        # Sort into appropriate list
        if is_available:
            available_categories.append(category)
        else:
            unavailable_categories.append(category)
    
    # Combine lists with available categories first
    sorted_categories = available_categories + unavailable_categories
    
    context = {
        'categories': sorted_categories,  # Use the sorted list instead of the original queryset
        'items': items,
        'room': room,
        'user': user,
    }
    
    return render(request, 'UserMenu.html', context)


def room_service_navigation(request, room_id, user_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    return render(request, 'UserNav.html', {'room': room, 'user': user})


@csrf_exempt
def request_room_service(request, room_id, user_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        service_id = data.get('service_id')

        

        user = get_object_or_404(User, id=user_id)
        room = get_object_or_404(Room, id=room_id, user=user)
        service_type = ServiceType.objects.get(id=service_id)
        RoomServiceRequest.objects.create(room=room, user=user, service_type=service_type)
        return JsonResponse({"message": "Room service requested successfully."})
