from django.urls import path
from . import views

urlpatterns = [
    # User settings views
    path('settings/', views.user_settings_view, name='user_settings_view'),
    path('settings/update/', views.update_settings, name='update_settings'),
    
    # Service type management
    path('service-types/', views.service_type_list, name='service_type_list'),
    path('service-types/add/', views.add_service_type, name='add_service_type'),
    path('service-types/delete/<int:service_id>/', views.delete_service_type, name='delete_service_type'),
]