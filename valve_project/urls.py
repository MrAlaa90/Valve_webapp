"""
URL configuration for valve_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views # مهم جداً لاستيراد الـ views الجاهزة
from valves.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('valves.urls')),
        # مسارات الـ API
    # أي request يبدأ بـ 'api/' هيتبعت لتطبيق 'valves' عشان يدور فيه
    # ده هيخلي الـ API URLs تكون بالشكل التالي:
    # http://127.0.0.1:8000/api/valves/
    # http://127.0.0.1:8000/api/valves/1/
    path('api/', include('valves.urls')), # **هذا هو التعديل الرئيسي**
    path('login/', auth_views.LoginView.as_view(template_name='valves/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),# الصفحة الرئيسية فقط
    path('', home, name='home'), 
    path('valves-frontend/', home, name='valve-list-frontend'),  # Frontend URLs
    path('maintenance-history-frontend/', home, name='maintenance-history-frontend'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # ضروري للصور