from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Import Django's auth views
from .views import CustomLoginView # Import your custom login view

app_name = 'valves' # Namespace for your app's URLs

urlpatterns = [
    # The root path for the 'valves' app will point to the home view
    path('', views.home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='valves:home'), name='logout'),
    
    # Frontend Views URLs
    path('valves-list/', views.valve_list_frontend, name='valve-list-frontend'),
    path('valves/create/', views.valve_create_frontend, name='valve-create-frontend'),
    path('valves/<int:pk>/', views.valve_detail_frontend, name='valve-detail-frontend'),
    path('valves/<int:pk>/update/', views.valve_update_frontend, name='valve-update-frontend'),
    path('valves/<int:pk>/delete/', views.valve_delete_frontend, name='valve-delete-frontend'),
    
    path('maintenance-history/', views.maintenance_history_frontend, name='maintenance-history-frontend'),
    path('maintenance/create/', views.maintenance_form_frontend, name='maintenance-create-frontend'),
    path('maintenance/<int:pk>/update/', views.maintenance_form_frontend, name='maintenance-update-frontend'),



    path('part-codes-list/', views.part_code_list_frontend, name='part-code-list-frontend'),
    path('part-codes/create/', views.part_code_form_frontend, name='part-code-create-frontend'),
    path('part-codes/<int:pk>/update/', views.part_code_form_frontend, name='part-code-update-frontend'),

    # API Endpoints (from rest_framework)
    path('api/valves/', views.ValveList.as_view(), name='valve-list-api'),
    path('api/valves/<int:pk>/', views.ValveDetail.as_view(), name='valve-detail-api'),
    path('api/get-valves-by-factory/', views.get_valves_by_factory, name='get-valves-by-factory'),
    path('api/valve-tag-autocomplete/', views.valve_tag_autocomplete, name='valve-tag-autocomplete'),

    path('api/part-codes/', views.PartCodeList.as_view(), name='part-code-list-api'),
    path('api/part-codes/<int:pk>/', views.PartCodeDetail.as_view(), name='part-code-detail-api'),
    path('api/maintenance-history/', views.MaintenanceHistoryList.as_view(), name='maintenance-history-list-api'),
    path('api/maintenance-history/<int:pk>/', views.MaintenanceHistoryDetail.as_view(), name='maintenance-history-detail-api'),
    path('api/maintenance-parts/', views.MaintenancePartList.as_view(), name='maintenance-part-list-api'),
    path('api/maintenance-parts/<int:pk>/', views.MaintenancePartDetail.as_view(), name='maintenance-part-detail-api'),

    # Placeholder URLs for missing views
    path('maintenance/<int:pk>/', views.maintenance_detail_frontend, name='maintenance-detail-frontend'),
    path('part-codes/<int:pk>/', views.part_code_detail_frontend, name='part-code-detail-frontend'),
    path('valves/<int:pk>/images/', views.valve_images_gallery_frontend, name='valve-images-gallery-frontend'),

    path('shutdown-report/', views.shutdown_report, name='shutdown-report'),
    path('shutdown-report/<int:pk>/print/', views.shutdown_report_print, name='shutdown-report-print'),
    path('part-codes/<int:pk>/delete/', views.part_code_delete_frontend, name='part-code-delete-frontend'),
    path('documents/', views.documents_page, name='documents-page'),
]