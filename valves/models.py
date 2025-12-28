import os
from django.db import models

def get_valve_image_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/valves/<tag_number>/<category>/<filename>
    return os.path.join('valves', instance.valve.tag_number, instance.category, filename)

def get_maintenance_image_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/maintenance/<valve_tag_number>/<maintenance_id>/<filename>
    return os.path.join('maintenance', instance.valve.tag_number, str(instance.maintenance_id), filename)

class ValveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class ValveStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

    def get_status_color(self):
        """Returns a Bootstrap color class based on the status name."""
        name_lower = self.name.lower()
        if 'operational' in name_lower or 'good' in name_lower:
            return 'success'
        elif 'needs maintenance' in name_lower or 'fair' in name_lower:
            return 'warning'
        elif 'critical' in name_lower or 'out of service' in name_lower:
            return 'danger'
        return 'secondary' # Default color

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Technician(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Factory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_color(self):
        """Returns a Bootstrap color class based on the factory name."""
        if self.name == 'AFC I':
            return 'danger'
        elif self.name == 'AFC II':
            return 'success'
        elif self.name == 'AFC III':
            return 'primary'
        # Default for ZLD or any other factory
        return 'info'

class Valve(models.Model):
    valve_id = models.AutoField(primary_key=True)
    tag_number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    valve_type = models.ForeignKey(ValveType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(ValveStatus, on_delete=models.SET_NULL, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True)
    factory = models.ForeignKey(Factory, on_delete=models.SET_NULL, null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    drawing_link = models.URLField(max_length=500, null=True, blank=True)
    model_number = models.CharField(max_length=255, null=True, blank=True)
    shut_off_pressure = models.CharField(max_length=255, null=True, blank=True)
    power_failure_pos = models.CharField(max_length=255, null=True, blank=True)
    body_style = models.CharField(max_length=255, null=True, blank=True)
    required_travel_angle = models.CharField(max_length=255, null=True, blank=True)
    bench_range = models.CharField(max_length=255, null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.tag_number

class Shutdown(models.Model):
    name = models.CharField(max_length=255)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    valves = models.ManyToManyField(Valve)
    def __str__(self):
        return self.name



class SparePart(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True, unique=True)
    part_name = models.CharField(max_length=255)

    def __str__(self):
        return self.part_name

class PartCode(models.Model):
    part_code_id = models.AutoField(primary_key=True)
    sap_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    oracle_code = models.CharField(max_length=100, null=True, blank=True)
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    unit_price = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    associated_valves = models.ManyToManyField(Valve, blank=True, related_name='part_codes')
    condition = models.CharField(max_length=255, null=True, blank=True)
    part_number = models.CharField(max_length=100, null=True, blank=True)
    manufacturer_co = models.CharField(max_length=255, null=True, blank=True)
    unit_of_measure = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.sap_code or self.oracle_code or self.part_number

class MaintenanceHistory(models.Model):
    maintenance_id = models.AutoField(primary_key=True)
    valve = models.ForeignKey(Valve, on_delete=models.CASCADE, related_name='maintenance_records')
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True)
    maintenance_date = models.DateField()
    oracle_code = models.CharField(max_length=255, null=True, blank=True)
    maintenance_activities = models.CharField(max_length=500, blank=True, null=True)
    maintenance_notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    before_image = models.ImageField(upload_to=get_maintenance_image_upload_path, verbose_name="Before Image", null=True, blank=True)
    after_image = models.ImageField(upload_to=get_maintenance_image_upload_path, verbose_name="After Image", null=True, blank=True)

    def __str__(self):
        return f"Maintenance for {self.valve.tag_number} on {self.maintenance_date}"

class MaintenancePart(models.Model):
    maintenance_part_id = models.AutoField(primary_key=True)
    maintenance_event = models.ForeignKey(MaintenanceHistory, on_delete=models.CASCADE)
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    code = models.ForeignKey(PartCode, on_delete=models.CASCADE)

class ValveImage(models.Model):
    IMAGE_CATEGORIES = [
        ('Valves_Specs', 'Valve Specs'),
        ('P&ID', 'P&ID'),
        ('Maintenance_Reports', 'Maintenance Reports'),
    ]
    valve = models.ForeignKey(Valve, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_valve_image_upload_path, verbose_name="Image")
    category = models.CharField(max_length=100, choices=IMAGE_CATEGORIES, default='Valves_Specs', verbose_name="Image Category")
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.valve.tag_number} - {self.get_category_display()}"
