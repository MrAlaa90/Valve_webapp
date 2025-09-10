from django.db import models

# Valve model 
class Valve(models.Model):
    valve_id = models.CharField(max_length=100, unique=True, primary_key=True)
    drawing_link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.valve_id

# Spare part model 
class SparePart(models.Model):
     part_id = models.CharField(max_length=100, unique=True, primary_key=True)
     part_name = models.CharField(max_length=255)

     def __str__(self):
         return self.part_name

# Part code model 
class PartCode(models.Model):
     code_id = models.CharField(max_length=100, unique=True, primary_key=True)
     part = models.ForeignKey(SparePart, on_delete=models.CASCADE)

     def __str__(self):
         return self.code_id

# Maintenance history model 
class MaintenanceHistory(models.Model):
     maintenance_id = models.AutoField(primary_key=True)
     valve = models.ForeignKey(Valve, on_delete=models.CASCADE)
     technician_name = models.CharField(max_length=255)
     maintenance_date = models.DateField()
     before_image = models.ImageField(upload_to='maintenance_images/')
     after_image = models.ImageField(upload_to='maintenance_images/')

     def __str__(self):
         return f'Maintenance on {self.valve.valve_id} on {self.maintenance_date}'

# Maintenance part model
class MaintenancePart(models.Model):
     maintenance_part_id = models.AutoField(primary_key=True)
     maintenance_event = models.ForeignKey(MaintenanceHistory, on_delete=models.CASCADE)
     part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
     code = models.ForeignKey(PartCode, on_delete=models.CASCADE)

     def __str__(self):
         return f'{self.part.part_name} used in maintenance event {self.maintenance_event.maintenance_id}'
