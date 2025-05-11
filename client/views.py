import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

# rooms/views.py
from .models import Room, RoomServiceRequest, ServiceAvailability
from menu.models import MenuItem
from django.contrib.auth.models import User


def room_service_interface(request, room_id, user_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    items = MenuItem.objects.filter(user=user)
    available_services = ServiceAvailability.objects.filter(is_available=True)
    return render(request, 'UserService.html', {'items': items, 'room': room, 'available_services': available_services, 'user': user})


def room_menu_interface(request, room_id, user_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    items = MenuItem.objects.filter(user=user)
    return render(request, 'UserMenu.html', {'items': items, 'room': room, 'user': user})


def room_service_navigation(request, room_id, user_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    return render(request, 'UserNav.html', {'room': room, 'user': user})


@csrf_exempt
def request_room_service(request, room_id, user_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        service_type = data.get('service_type')

        if service_type not in dict(RoomServiceRequest.SERVICE_TYPE_CHOICES):
            return JsonResponse({"error": "Invalid service type."}, status=400)

        user = get_object_or_404(User, id=user_id)
        room = get_object_or_404(Room, id=room_id, user=user)
        RoomServiceRequest.objects.create(room=room, user=user, service_type=service_type)
        return JsonResponse({"message": "Room service requested successfully."})
