from django.urls import path
from .import views
from django.contrib.auth.decorators import login_required

# استدعاء Views الخاصة بالـ API (نقطة الوصول للبيانات)
# استدعاء Views الخاصة بالـ API (نقطة الوصول للبيانات)
from .views import (
    ValveList, ValveDetail, SparePartList, SparePartDetail,
    PartCodeList, PartCodeDetail, MaintenanceHistoryList,
    MaintenanceHistoryDetail, MaintenancePartList, MaintenancePartDetail,
)
# استدعاء Views الخاصة بالـ Frontend (واجهة المستخدم)
from .views import (
    valve_list_frontend, valve_create_frontend, valve_detail_frontend,
    valve_update_frontend, valve_delete_frontend, 
    maintenance_history_frontend, 
    spare_part_list_frontend, part_code_list_frontend,

     # الدوال الجديدة التي تم نسيان استيرادها أو تفعيلها
    spare_part_form_frontend, 
    part_code_form_frontend,
    maintenance_form_frontend, # <--- تم إضافة استيراد دالة نموذج الصيانة
)

app_name = 'valves'

# قائمة الـ URLs الخاصة بالـ API
api_urlpatterns = [
     # 1. مسار الجذر /valves/ - يوجه مباشرة لقائمة البلوف
    path('', views.valve_list_frontend, name='valve-list-frontend'), # <-- هذا هو المسار الجديد الذي سيحل مشكلة الـ 404
    # API Endpoints (هذه موجودة بالفعل، تم تجميعها لمزيد من التنظيم)
    path('api/valves/', ValveList.as_view(), name='valve-list'),
    path('api/valves/<int:pk>/', ValveDetail.as_view(), name='valve-detail'),
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
    # 1. البلوف (Valves)
    # path('list/', views.valve_list_frontend, name='valve-list-frontend'),
    path('create/', views.valve_create_frontend, name='valve-create-frontend'),
    path('<int:pk>/',views.valve_detail_frontend, name='valve-detail-frontend'),
    path('<int:pk>/update/', views.valve_update_frontend, name='valve-update-frontend'),
    path('<int:pk>/delete/', views.valve_delete_frontend, name='valve-delete-frontend'),
    # 2. سجل الصيانة (Maintenance History)
    path('maintenance-history/', views.maintenance_history_frontend, name='maintenance-history-frontend'),
    path('maintenance-history/create/', views.maintenance_form_frontend, name='maintenance-create-frontend'), # سنبنيها لاحقاً
    path('maintenance-history/<int:pk>/update/', views.maintenance_form_frontend, name='maintenance-update-frontend'), 

    # 3. قطع الغيار (Spare Parts)
    path('spare-parts/', views.spare_part_list_frontend, name='spare-part-list-frontend'),
    path('spare-parts/create/', spare_part_form_frontend, name='spare-part-create-frontend'),
    path('spare-parts/<int:pk>/update/', spare_part_form_frontend, name='spare-part-update-frontend'),
    # path('spare-parts/<int:pk>/delete/', views.spare_part_delete_frontend, name='spare-part-delete-frontend'),
    
    # 4. أكواد القطع (Part Codes)
    path('part-codes/', views.part_code_list_frontend, name='part-code-list-frontend'),
    path('part-codes/create/', part_code_form_frontend, name='part-code-create-frontend'),
    path('part-codes/<int:pk>/update/', part_code_form_frontend, name='part-code-update-frontend'),
    # path('part-codes/<int:pk>/delete/', views.part_code_delete_frontend, name='part-code-delete-frontend'),
]

# دمج القائمتين في قائمة واحدة
urlpatterns = api_urlpatterns + frontend_urlpatterns

