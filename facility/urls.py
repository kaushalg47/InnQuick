# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('facilities/', views.facilities_dashboard, name='facilities_dashboard'),
    path('bookings/', views.mobile_facilities, name='booking_list'),
    path('bookings/pos/', views.pos_facilities, name='booking_list'),
    path('bookings/time-slots/<int:facility_id>/', views.get_facility_slots, name='get_facility_slots'),
    path('create-booking/<int:facility_id>', views.create_booking, name='create_booking'),

    path('all-bookings/', views.view_all_bookings, name='view_all_bookings'),
    path('all-bookings/<int:booking_id>/settle/', views.settle_booking, name='settle_booking'),
    path('all-bookings/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),

    path('get-it/', views.get_all_bookings, name='get_all_bookings'),
]