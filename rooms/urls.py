# rooms/urls.py

from django.urls import path
from . import views
from.views import admin_dashboard

urlpatterns = [
    path('login', views.admin_login, name='admin_login'),
    path('logout', views.admin_logout, name='admin_logout'),
    path('dashboard', admin_dashboard, name='admin_dashboard'),
    path('add-room', views.add_room, name='add_room'),
    path('<int:room_id>/delete-room', views.delete_room, name='delete_room'),
    path('dashboard/get-room', views.fetch_rooms, name='fetch_rooms'),
    path('dashboard/requests', views.get_room_service_requests, name='get_room_service_requests'),
    path('dashboard/requests/<int:request_id>/mark-serviced', views.mark_as_serviced, name='mark-as-serviced'),
    path('dashboard/manage-services', views.manage_services, name='manage_services'),
]
