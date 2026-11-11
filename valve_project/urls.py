"""
URL configuration for valve_project project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

# Explicit imports to ensure PyInstaller bundles dynamic URL configs
import djoser.urls
import djoser.urls.authtoken
import rest_framework.urls
import django.conf.urls.i18n

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # For browsable API login
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('', include('valves.urls')),  # Include the valves app URLs at the root
    # Ensure media files are accessible in Desktop standalone mode and development
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
