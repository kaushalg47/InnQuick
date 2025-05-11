import base64
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Room
from client.models import RoomServiceRequest, ServiceAvailability
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


@login_required
def manage_services(request):
    # Fetch all service availability records
    services = ServiceAvailability.objects.all()

    if request.method == 'POST':
        # Iterate over the services to update availability based on POST data
        for service in services:
            service.is_available = f"service_{service.id}" in request.POST
            service.save()
        # After saving, redirect to the same page to show the updated status
        return redirect('manage_services')

    # Render the template with the services context
    return render(request, 'ManageServices.html', {'services': services})
