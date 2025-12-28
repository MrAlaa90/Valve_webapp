"""
URL configuration for valve_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')), # For browsable API login
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('', include('valves.urls')),  # Include the valves app URLs at the root
]

# Serve media files during development
if settings.DEBUG:
    print(f"DEBUG: MEDIA_URL={settings.MEDIA_URL}, MEDIA_ROOT={settings.MEDIA_ROOT}")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)