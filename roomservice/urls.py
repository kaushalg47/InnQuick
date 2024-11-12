# roomservice/urls.py

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rooms import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rooms/', include('rooms.urls')),
    path('client/', include('client.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
