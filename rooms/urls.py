# rooms/urls.py

from django.urls import path
from . import views
from.views import admin_dashboard

urlpatterns = [
    path('admin/login', views.admin_login, name='admin_login'),
    path('admin/logout', views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/add-room', views.add_room, name='add_room'),
    path('admin/<int:room_id>/delete-room/', views.delete_room, name='delete_room'),
    path('admin/dashboard/get-room', views.fetch_rooms, name='fetch_rooms'),
    path('admin/dashboard/requests/', views.get_room_service_requests, name='get_room_service_requests'),
    path('admin/dashboard/requests/<int:request_id>/mark-serviced/', views.mark_as_serviced, name='mark-as-serviced'),
    path('admin/dashboard/manage-services/', views.manage_services, name='manage_services'),
]
