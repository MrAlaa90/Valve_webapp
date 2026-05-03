from django.contrib import admin
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart, ValveType, ValveStatus, Manufacturer, Technician, Shutdown

@admin.register(Valve)
class ValveAdmin(admin.ModelAdmin):
    list_display = ('tag_number', 'name', 'valve_type', 'status', 'factory')
    list_filter = ('valve_type', 'status', 'factory')
    search_fields = ('tag_number', 'name')
    fieldsets = (
        (None, {
            'fields': ('tag_number', 'name', 'location', 'factory', 'valve_type', 'status', 'manufacturer', 'model_number')
        }),
        ('Technical Specifications', {
            'fields': (
                'shut_off_pressure', 'power_failure_pos', 'body_style', 
                'required_travel_angle', 'bench_range', 'plug_stem_mat', 
                'butterfly_shaft_mat', 'seat_guide_mat', 'seat_diameter', 
                'trim_coating', 'leakage_class', 'packing_mat'
            )
        }),
        ('Additional Information', {
            'fields': ('installation_date', 'last_maintenance_date', 'notes', 'drawing_link', 'sort_order')
        }),
    )

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
