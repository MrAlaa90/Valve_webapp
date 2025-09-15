from rest_framework import serializers
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart

class ValveSerializer(serializers.ModelSerializer):
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
            'drawing_link'
            ]
        read_only_fields = ['valve_id']
        # لو كنت عامل fields = '__all__'، يبقى الـ id هيظهر تلقائياً
        # لكن الأفضل دايماً تحدد الحقول صراحة.

class SparePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePart
        fields = '__all__'

class PartCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartCode
        fields = '__all__'

class MaintenanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceHistory
        fields = '__all__'

class MaintenancePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenancePart
        fields = '__all__'