# roomservice/urls.py

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rooms import views
from roomservice.views import home
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('rooms/', include('rooms.urls')),
    path('client/', include('client.urls')),
    path('menu/', include('menu.urls')),
    path('core/', include('core.urls')),
    path('facility/', include('facility.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
