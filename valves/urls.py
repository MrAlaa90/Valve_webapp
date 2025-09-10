from django.urls import path
from .views import ValveList, ValveDetail, SparePartList, SparePartDetail, PartCodeList, PartCodeDetail, MaintenanceHistoryList, MaintenanceHistoryDetail, MaintenancePartList, MaintenancePartDetail

urlpatterns = [
    path('valves/', ValveList.as_view(), name='valve-list'),
    path('valves/<str:pk>/', ValveDetail.as_view(), name='valve-detail'),
    path('spare-parts/', SparePartList.as_view(), name='spare-part-list'),
    path('spare-parts/<str:pk>/', SparePartDetail.as_view(), name='spare-part-detail'),
    path('part-codes/', PartCodeList.as_view(), name='part-code-list'),
    path('part-codes/<str:pk>/', PartCodeDetail.as_view(), name='part-code-detail'),
    path('maintenance-history/', MaintenanceHistoryList.as_view(), name='maintenance-history-list'),
    path('maintenance-history/<int:pk>/', MaintenanceHistoryDetail.as_view(), name='maintenance-history-detail'),
    path('maintenance-parts/', MaintenancePartList.as_view(), name='maintenance-parts-list'),
    path('maintenance-parts/<int:pk>/', MaintenancePartDetail.as_view(), name='maintenance-parts-detail'),
]
