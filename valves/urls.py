from django.urls import path
from .import views
# استدعاء Views الخاصة بالـ API (نقطة الوصول للبيانات)
from .views import ValveList, ValveDetail, SparePartList, SparePartDetail, PartCodeList, PartCodeDetail, MaintenanceHistoryList, MaintenanceHistoryDetail, MaintenancePartList, MaintenancePartDetail, home, valve_list_frontend, valve_create_frontend, valve_detail_frontend, valve_update_frontend
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView # هنستخدمها كـ View مؤقتة

# قائمة الـ URLs الخاصة بالـ API
api_urlpatterns = [
    path('api/valves/', ValveList.as_view(), name='valve-list'),
    path('api/valves/<str:pk>/', ValveDetail.as_view(), name='valve-detail'),
    path('api/spare-parts/', SparePartList.as_view(), name='spare-part-list'),
    path('api/spare-parts/<str:pk>/', SparePartDetail.as_view(), name='spare-part-detail'),
    path('api/part-codes/', PartCodeList.as_view(), name='part-code-list'),
    path('api/part-codes/<str:pk>/', PartCodeDetail.as_view(), name='part-code-detail'),
    path('api/maintenance-history/', MaintenanceHistoryList.as_view(), name='maintenance-history-list'),
    path('api/maintenance-history/<int:pk>/', MaintenanceHistoryDetail.as_view(), name='maintenance-history-detail'),
    path('api/maintenance-parts/', MaintenancePartList.as_view(), name='maintenance-parts-list'),
    path('api/maintenance-parts/<int:pk>/', MaintenancePartDetail.as_view(), name='maintenance-parts-detail'),
    ]


# قائمة الـ URLs الخاصة بالـ Frontend (واجهة المستخدم)
frontend_urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('valves/', login_required(views.valve_list_frontend), name='valve-list-frontend'),
    path('valves/create/', login_required(views.valve_create_frontend), name='valve-create-frontend'),
    path('valves/<int:pk>/', login_required(views.valve_detail_frontend), name='valve-detail-frontend'),
    path('valves/<int:pk>/update/', login_required(views.valve_update_frontend), name='valve-update-frontend'),
    path('valves/<int:pk>/delete/', login_required(views.valve_delete_frontend), name='valve-delete-frontend'),
    path('maintenance-history/', login_required(views.maintenance_history_frontend), name='maintenance-history-frontend'),
    path('spare-parts/', login_required(views.spare_part_list_frontend), name='spare-part-list-frontend'),
    path('part-codes/', login_required(views.part_code_list_frontend), name='part-code-list-frontend'),
]

# دمج القائمتين في قائمة واحدة
urlpatterns = api_urlpatterns + frontend_urlpatterns

