from django.contrib import admin
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart, ValveType, ValveStatus, Manufacturer, Technician, Shutdown

@admin.register(Valve)
class ValveAdmin(admin.ModelAdmin):
    list_display = ('tag_number', 'name', 'valve_type', 'status', 'factory')
    list_filter = ('valve_type', 'status', 'factory')
    search_fields = ('tag_number', 'name')

@admin.register(MaintenanceHistory)
class MaintenanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('maintenance_id', 'valve', 'maintenance_date', 'technician')
    list_filter = ('maintenance_date', 'technician')
    search_fields = ('valve__tag_number', 'maintenance_notes')

@admin.register(PartCode)
class PartCodeAdmin(admin.ModelAdmin):
    list_display = ('sap_code', 'description', 'quantity', 'location')
    list_filter = ('location', 'category')
    search_fields = ('sap_code', 'oracle_code', 'description')

admin.site.register(SparePart)
admin.site.register(MaintenancePart)
admin.site.register(ValveType)
admin.site.register(ValveStatus)
admin.site.register(Manufacturer)
admin.site.register(Technician)
admin.site.register(Shutdown)
