from django.contrib import admin
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart, ValveType, ValveStatus, Manufacturer, Technician, Shutdown

admin.site.register(Valve)
admin.site.register(SparePart)
admin.site.register(PartCode)
admin.site.register(MaintenanceHistory)
admin.site.register(MaintenancePart)
admin.site.register(ValveType)
admin.site.register(ValveStatus)
admin.site.register(Manufacturer)
admin.site.register(Technician)
admin.site.register(Shutdown)

