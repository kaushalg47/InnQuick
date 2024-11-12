# rooms/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('<int:room_id>/request-service/', views.request_room_service, name='request-room-service'),
    path('<int:room_id>/', views.room_service_interface, name="room-service-interface")
    
]
