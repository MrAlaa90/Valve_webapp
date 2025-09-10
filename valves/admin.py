from django.contrib import admin
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart

admin.site.register(Valve)
admin.site.register(SparePart)
admin.site.register(PartCode)
admin.site.register(MaintenanceHistory)
admin.site.register(MaintenancePart)

# Register your models here.
