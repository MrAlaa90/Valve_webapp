from django.contrib import messages # To show messages to the user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend # Added
from .models import (
    Valve, PartCode, MaintenanceHistory, MaintenancePart,
    Factory, ValveStatus, Shutdown, ValveType, Manufacturer, Technician
)
from .serializers import ValveSerializer, PartCodeSerializer, MaintenanceHistorySerializer, MaintenancePartSerializer
from .forms import ShutdownReportForm, MaintenanceHistoryForm
from django.core.paginator import Paginator
from django.db.models import Q
from .filters import PartCodeFilter # Added
from django.template.defaultfilters import slugify

class CustomLoginView(LoginView):
    template_name = 'registration/login.html' # Make sure this template exists
    redirect_authenticated_user = True

@login_required
def valve_detail_frontend(request, pk):
    """
    Display detailed information about a specific valve, including its maintenance history,
    spare parts, and related documents.
    """
    valve = get_object_or_404(
        Valve.objects.select_related(
            'valve_type', 'status', 'manufacturer', 'factory'
        ).prefetch_related(
            'images',
            'maintenance_records',
            'part_codes'
        ), 
        pk=pk
    )
    
    # Get maintenance records ordered by date
    maintenance_records = valve.maintenance_records.all().order_by('-maintenance_date')
    
    # Get associated part codes (directly linked to the valve)
    related_part_codes = valve.part_codes.all()

    # Get parts used in maintenance history
    parts_used_in_history = []
    for record in maintenance_records:
        parts_used_in_history.extend(record.maintenancepart_set.all())
    
    context = {
        'valve': valve,
        'maintenance_records': maintenance_records,
        'related_part_codes': related_part_codes,
        'parts_used_in_history': parts_used_in_history,
    }
    return render(request, 'valves/valve_detail.html', context)

@login_required
def valve_create_frontend(request):
    """
    Handle creation of a new valve through the frontend interface.
    GET: Display the valve creation form
    POST: Process the submitted form and create a new valve
    """
    if request.method == 'POST':
        # Extract form data
        tag_number = request.POST.get('tag_number')
        name = request.POST.get('name')
        serial_number = request.POST.get('serial_number')
        valve_type_id = request.POST.get('valve_type')
        status_id = request.POST.get('status')
        manufacturer_id = request.POST.get('manufacturer')
        factory_id = request.POST.get('factory')
        location = request.POST.get('location')
        description = request.POST.get('description')

        try:
            # Create new valve object
            valve = Valve.objects.create(
                tag_number=tag_number,
                name=name,
                serial_number=serial_number,
                valve_type_id=valve_type_id,
                status_id=status_id,
                manufacturer_id=manufacturer_id,
                factory_id=factory_id,
                location=location,
                description=description
            )
            messages.success(request, f'Valve {valve.tag_number} was created successfully.')
            return redirect('valve-detail-frontend', pk=valve.pk)
        except Exception as e:
            messages.error(request, f'Error creating valve: {str(e)}')
            return redirect('valve-create-frontend')

    # For GET requests, prepare the form context
    context = {
        'valve_types': ValveType.objects.all().order_by('name'),
        'statuses': ValveStatus.objects.all().order_by('name'),
        'manufacturers': Manufacturer.objects.all().order_by('name'),
        'factories': Factory.objects.all().order_by('name'),
    }
    return render(request, 'valves/valve_form.html', context)

@login_required
def valve_list_frontend(request):
    """
    Handles the frontend display of a list of valves with filtering, searching, and pagination.
    """
    valves_list = Valve.objects.select_related('valve_type', 'status', 'manufacturer', 'factory').all().order_by('tag_number')
    
    factories = Factory.objects.all().order_by('name')
    statuses = ValveStatus.objects.all().order_by('name')

    selected_factory_slug = request.GET.get('factory', '')
    selected_status = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    # Filtering
    if selected_factory_slug:
        try:
            # Find the factory by its slugified name
            factory_obj = next(f for f in factories if slugify(f.name) == selected_factory_slug)
            valves_list = valves_list.filter(factory=factory_obj)
        except StopIteration:
            # Handle case where slug doesn't match any factory
            pass
            
    if selected_status:
        valves_list = valves_list.filter(status__name=selected_status)

    # Searching
    if search_query:
        valves_list = valves_list.filter(
            Q(tag_number__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(valve_type__name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(valves_list, 15)  # Show 15 valves per page
    page_number = request.GET.get('page')
    valves = paginator.get_page(page_number)

    context = {
        'valves': valves,
        'factories': factories,
        'statuses': statuses,
        'selected_factory': selected_factory_slug,
        'selected_status': selected_status,
        'search_query': search_query,
    }
    return render(request, 'valves/valve_list.html', context)

@login_required
def home(request):
    """
    View for the home page, displaying dashboard with valve statistics.
    """
    try:
        factories = Factory.objects.all()
        main_factories = []
        zld_factory = None
        
        for factory in factories:
            factory_valves = Valve.objects.filter(factory=factory)
            factory.total_valves = factory_valves.count()
            factory.operational_valves = factory_valves.filter(status__name='Operational').count()
            factory.needs_maintenance_valves = factory_valves.filter(status__name='Needs Maintenance').count()
            
            if 'ZLD' in factory.name.upper():
                zld_factory = factory
            else:
                main_factories.append(factory)

        recent_maintenance = MaintenanceHistory.objects.all().order_by('-maintenance_date')[:5]
        recent_valves = Valve.objects.all().order_by('-valve_id')[:5]

    except Exception as e:
        messages.error(request, f"Error loading dashboard data: {str(e)}")
        main_factories = []
        zld_factory = None
        recent_maintenance = []
        recent_valves = []

    context = {
        'main_factories': main_factories,
        'zld_factory': zld_factory,
        'recent_maintenance': recent_maintenance,
        'recent_valves': recent_valves,
    }
    return render(request, 'valves/home.html', context)

class ValveList(generics.ListCreateAPIView):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer

class ValveDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer




class PartCodeList(generics.ListCreateAPIView):
    queryset = PartCode.objects.all()
    serializer_class = PartCodeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PartCodeFilter

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

from django.urls import reverse
from django.http import HttpResponseRedirect
...
@login_required
def maintenance_form_frontend(request, pk=None):
    """
    View for creating and updating maintenance records.
    """
    record = None
    valve_instance = None
    initial_data = {}
    technicians = Technician.objects.all().order_by('name')

    if pk:
        # Update an existing record
        record = get_object_or_404(MaintenanceHistory, pk=pk)
        valve_instance = record.valve
    else:
        # Create a new record
        valve_id = request.GET.get('valve_id')
        if valve_id:
            valve_instance = get_object_or_404(Valve, pk=valve_id)
            initial_data['valve_tag_number'] = valve_instance.tag_number

    if request.method == 'POST':
        form = MaintenanceHistoryForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            instance = form.save()
            messages.success(request, "Maintenance record saved successfully!")
            redirect_url = reverse('valves:valve-detail-frontend', kwargs={'pk': instance.valve.pk})
            return HttpResponseRedirect(redirect_url + '#maintenance-pane')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MaintenanceHistoryForm(instance=record, initial=initial_data)

    title = "Update Maintenance Record" if pk else "Create New Maintenance Record"
    context = {
        'form': form,
        'title': title,
        'pk': pk,
        'valve': valve_instance,
        'technicians': technicians
    }
    return render(request, 'valves/maintenance_form.html', context)

@login_required
def valve_update_frontend(request, pk):
    """
    Handle updating an existing valve through the frontend interface.
    """
    valve = get_object_or_404(Valve, pk=pk)
    
    if request.method == 'POST':
        try:
            # Update valve data
            valve.tag_number = request.POST.get('tag_number')
            valve.name = request.POST.get('name')
            valve.serial_number = request.POST.get('serial_number')
            valve.valve_type_id = request.POST.get('valve_type')
            valve.status_id = request.POST.get('status')
            valve.manufacturer_id = request.POST.get('manufacturer')
            valve.factory_id = request.POST.get('factory')
            valve.location = request.POST.get('location')
            valve.description = request.POST.get('description')
            valve.save()
            
            messages.success(request, f'Valve {valve.tag_number} was updated successfully.')
            return redirect('valve-detail-frontend', pk=valve.pk)
        except Exception as e:
            messages.error(request, f'Error updating valve: {str(e)}')
    
    context = {
        'valve': valve,
        'valve_types': ValveType.objects.all().order_by('name'),
        'statuses': ValveStatus.objects.all().order_by('name'),
        'manufacturers': Manufacturer.objects.all().order_by('name'),
        'factories': Factory.objects.all().order_by('name'),
    }
    return render(request, 'valves/valve_form.html', context)

@login_required
def valve_delete_frontend(request, pk):
    """
    Handle deletion of a valve.
    """
    valve = get_object_or_404(Valve, pk=pk)
    
    if request.method == 'POST':
        try:
            valve.delete()
            messages.success(request, f'Valve {valve.tag_number} was deleted successfully.')
            return redirect('valve-list-frontend')
        except Exception as e:
            messages.error(request, f'Error deleting valve: {str(e)}')
            return redirect('valve-detail-frontend', pk=pk)
    
    context = {'valve': valve}
    return render(request, 'valves/valve_confirm_delete.html', context)

@login_required
def maintenance_history_frontend(request):
    """
    Display list of all maintenance records with filtering and pagination.
    """
    maintenance_list = MaintenanceHistory.objects.select_related(
        'valve'
    ).order_by('-maintenance_date')
    
    search_query = request.GET.get('q', '')
    if search_query:
        maintenance_list = maintenance_list.filter(
            Q(valve__tag_number__icontains=search_query) |
            Q(maintenance_type__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(maintenance_list, 15)
    page_number = request.GET.get('page')
    maintenance_records = paginator.get_page(page_number)
    
    context = {
        'maintenance_records': maintenance_records,
        'search_query': search_query,
    }
    return render(request, 'valves/maintenance_list.html', context)

@login_required
def maintenance_detail_frontend(request, pk):
    """
    Display detailed information about a specific maintenance record.
    """
    maintenance = get_object_or_404(
        MaintenanceHistory.objects.select_related('valve'),
        pk=pk
    )
    
    context = {
        'record': maintenance,
        'parts_used': maintenance.maintenancepart_set.all(),
    }
    return render(request, 'valves/maintenance_detail.html', context)

@login_required
def part_code_list_frontend(request):
    """
    Display list of all part codes with filtering and pagination.
    """
    part_codes_list = PartCode.objects.all().order_by('sap_code')
    
    search_query = request.GET.get('q', '')
    if search_query:
        part_codes_list = part_codes_list.filter(
            Q(sap_code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(part_codes_list, 15)
    page_number = request.GET.get('page')
    part_codes = paginator.get_page(page_number)
    
    context = {
        'part_codes': part_codes,
        'search_query': search_query,
    }
    return render(request, 'valves/part_code_list.html', context)

@login_required
def part_code_form_frontend(request, pk=None):
    """
    Handle creation and updating of part codes.
    """
    if pk:
        part_code = get_object_or_404(PartCode, pk=pk)
        title = "Update Part Code"
    else:
        part_code = None
        title = "Create New Part Code"
    
    if request.method == 'POST':
        try:
            if part_code:
                # Update existing part code
                part_code.sap_code = request.POST.get('code')
                part_code.description = request.POST.get('description')
                part_code.save()
                messages.success(request, f'Part code {part_code.sap_code} was updated successfully.')
            else:
                # Create new part code
                part_code = PartCode.objects.create(
                    sap_code=request.POST.get('code'),
                    description=request.POST.get('description')
                )
                messages.success(request, f'Part code {part_code.sap_code} was created successfully.')
            return redirect('part-code-detail-frontend', pk=part_code.pk)
        except Exception as e:
            messages.error(request, f'Error saving part code: {str(e)}')
    
    context = {
        'part_code': part_code,
        'title': title,
    }
    return render(request, 'valves/part_code_form.html', context)

@login_required
def part_code_detail_frontend(request, pk):
    """
    Display detailed information about a specific part code.
    """
    part_code = get_object_or_404(PartCode, pk=pk)
    
    context = {
        'part_code': part_code,
        'valves': part_code.valves.all(),
    }
    return render(request, 'valves/part_code_detail.html', context)

@login_required
def part_code_delete_frontend(request, pk):
    """
    Handle deletion of a part code.
    """
    part_code = get_object_or_404(PartCode, pk=pk)
    
    if request.method == 'POST':
        try:
            part_code.delete()
            messages.success(request, f'Part code {part_code.sap_code} was deleted successfully.')
            return redirect('part-code-list-frontend')
        except Exception as e:
            messages.error(request, f'Error deleting part code: {str(e)}')
            return redirect('part-code-detail-frontend', pk=pk)
    
    context = {'part_code': part_code}
    return render(request, 'valves/part_code_confirm_delete.html', context)

@login_required
def valve_images_gallery_frontend(request, pk):
    """
    Display image gallery for a specific valve.
    """
    valve = get_object_or_404(
        Valve.objects.prefetch_related('images'),
        pk=pk
    )
    
    context = {
        'valve': valve,
        'images': valve.images.all(),
    }
    return render(request, 'valves/valve_gallery.html', context)

@login_required
def shutdown_report(request):
    """
    Handle creation and display of shutdown reports.
    """
    if request.method == 'POST':
        form = ShutdownReportForm(request.POST)
        if form.is_valid():
            shutdown = form.save()
            messages.success(request, 'Shutdown report created successfully.')
            return redirect('shutdown-report-print', pk=shutdown.pk)
    else:
        form = ShutdownReportForm()
    
    context = {
        'form': form,
        'shutdowns': Shutdown.objects.all().order_by('-start_date')[:10]
    }
    return render(request, 'valves/shutdown_report.html', context)

@login_required
def shutdown_report_print(request):
    """
    Generate printable version of the shutdown report.
    """
    shutdowns = Shutdown.objects.all().order_by('-start_date')
    
    context = {
        'shutdowns': shutdowns,
        'print_mode': True
    }
    return render(request, 'valves/shutdown_report_print.html', context)