from django.urls import path
from .views import menu_list, place_order, order_list, mark_order_done, add_menu_item, completed_orders, delete_item, toggle_active, update_discount, create_category, toggle_category_active, update_category_discount

urlpatterns = [
    path('menu/', menu_list, name='menu_list'),
    path('place-order/', place_order, name='place_order'),
    path('orders/', order_list, name='order_list'),
    path('all-orders/', completed_orders, name='completed_orders'),
    path('orders/<int:order_id>/done/', mark_order_done, name='mark_order_done'),
    path('delete-item/<int:item_id>/', delete_item, name='delete_item'),
    path('add-item/', add_menu_item, name='add_menu_item'),
    path('toggle-active/<int:item_id>/', toggle_active, name='toggle_active'),
    path('update-discount/<int:item_id>/', update_discount, name='update_discount'),
    path('create-category/', create_category, name='create_category'),
    path('<int:category_id>/toggle-active/', toggle_category_active, name='toggle_category_active'),
    path('<int:category_id>/update-discount/', update_category_discount, name='update_category_discount'),

]