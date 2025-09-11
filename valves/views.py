from django.shortcuts import render
from rest_framework import generics
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart
from .serializers import ValveSerializer, SparePartSerializer, PartCodeSerializer, MaintenanceHistorySerializer, MaintenancePartSerializer

class ValveList(generics.ListCreateAPIView):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer

class ValveDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer

class SparePartList(generics.ListCreateAPIView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer

class SparePartDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer

class PartCodeList(generics.ListCreateAPIView):
    queryset = PartCode.objects.all()
    serializer_class = PartCodeSerializer

class PartCodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PartCode.objects.all()
    serializer_class = PartCodeSerializer

class MaintenanceHistoryList(generics.ListCreateAPIView):
    queryset = MaintenanceHistory.objects.all()
    serializer_class = MaintenanceHistorySerializer

class MaintenanceHistoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaintenanceHistory.objects.all()
    serializer_class = MaintenanceHistorySerializer

class MaintenancePartList(generics.ListCreateAPIView):
    queryset = MaintenancePart.objects.all()
    serializer_class = MaintenancePartSerializer

class MaintenancePartDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaintenancePart.objects.all()
    serializer_class = MaintenancePartSerializer 


def home(request):
    return render(request, 'valves/home.html')