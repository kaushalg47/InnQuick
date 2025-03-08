# rooms/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('<int:room_id>/request-service/', views.request_room_service, name='request-room-service'),
    path('<int:room_id>/', views.room_service_navigation, name='room-service-navigation'),
    path('<int:room_id>/menu/', views.room_menu_interface, name='room-menu-interface'),
    path('<int:room_id>/service/', views.room_service_interface, name="room-service-interface")
    
]
