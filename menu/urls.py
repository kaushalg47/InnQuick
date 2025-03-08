from django.urls import path
from .views import menu_list, place_order, order_list, mark_order_done, add_menu_item, completed_orders

urlpatterns = [
    path('menu/', menu_list, name='menu_list'),
    path('place-order/', place_order, name='place_order'),
    path('orders/', order_list, name='order_list'),
    path('all-orders/', completed_orders, name='completed_orders'),
    path('orders/<int:order_id>/done/', mark_order_done, name='mark_order_done'),
    path('add-item/', add_menu_item, name='add_menu_item'),
]