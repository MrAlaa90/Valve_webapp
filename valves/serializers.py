from rest_framework import serializers
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart

class ValveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valve
        fields = '__all__'

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