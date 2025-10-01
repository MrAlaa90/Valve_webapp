from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views # مهم جداً لاستيراد الـ views الجاهزة
from valves import views as valves_views
from valves.views import home
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView # هنستخدمها كـ View مؤقتة

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', valves_views.home, name='home'), 
    path('valves/', include(('valves.urls'), namespace='valves')), 
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),# الصفحة الرئيسية فقط
    # path('valves-frontend/', home, name='valve-list-frontend'),  # Frontend URLs
    # path('maintenance-history-frontend/', home, name='maintenance-history-frontend'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # ضروري للصور