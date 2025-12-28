from rest_framework import serializers
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart

class ValveSerializer(serializers.ModelSerializer):
    # 'images' field has been removed
    # images = ValveImageSerializer(many=True, read_only=True)
    class Meta:
        model = Valve
        fields = [
            'valve_id',
            'tag_number',
            'name',
            'location',
            'valve_type',
            'status',
            'installation_date',
            'last_maintenance_date',
            'notes',
            'drawing_link', # This field has been kept as it may not be an image
            # 'images' # images field has been removed
            ]
        read_only_fields = ['valve_id']
        # If you had fields = '__all__', the id would appear automatically
        # But it is always better to specify the fields explicitly.

class SparePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePart
        fields = '__all__'

class PartCodeSerializer(serializers.ModelSerializer):
    part = SparePartSerializer()
    class Meta:
        model = PartCode
        fields = '__all__'

class MaintenanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceHistory
        # The fields have been explicitly defined including the new fields for clarity
        fields = [
            'maintenance_id',
            'valve',
            'technician_name',
            'maintenance_date',
            'before_image',
            'after_image',
            'oracle_code',        # New field: Oracle code/order
            'maintenance_notes',  # New field: Detailed notes
            'is_active'           # New field: Maintenance status
        ]
        read_only_fields = ['maintenance_id']

class MaintenancePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenancePart
        fields = '__all__'