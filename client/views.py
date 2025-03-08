import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# rooms/views.py
from django.shortcuts import render, get_object_or_404
from .models import Room, RoomServiceRequest, ServiceAvailability
from menu.models import MenuItem


def room_service_interface(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    items = MenuItem.objects.filter(user=request.user)
    available_services = ServiceAvailability.objects.filter(is_available=True)
    # Render the service interface for residents
    return render(request, 'UserService.html', {'items': items, 'room': room, 'available_services': available_services})

def room_menu_interface(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    items = MenuItem.objects.filter(user=request.user)
    # Render the service interface for residents
    return render(request, 'UserMenu.html', {'items': items, 'room': room})

def room_service_navigation(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Render the service interface for residents
    return render(request, 'UserNav.html', {'room': room})
# Create your views here.
@csrf_exempt
def request_room_service(request, room_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        service_type = data.get('service_type')

        if service_type not in dict(RoomServiceRequest.SERVICE_TYPE_CHOICES):
            return JsonResponse({"error": "Invalid service type."}, status=400)
        room = Room.objects.get(id=room_id, user=request.user)
        RoomServiceRequest.objects.create(room=room, user=request.user, service_type=service_type)
        return JsonResponse({"message": "Room service requested successfully."})
