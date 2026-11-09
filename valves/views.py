import csv
import os
from django.conf import settings # Add this import
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
    
    # Get part codes directly associated with the valve
    basic_part_codes = valve.part_codes.all()
    
    # Get related part codes by part number
    selected_part_number = request.GET.get('part_number')
    if selected_part_number:
        part_numbers_to_match = [selected_part_number]
    else:
        part_numbers_to_match = [pc.part_number for pc in basic_part_codes if pc.part_number]

    part_number_related_codes = PartCode.objects.none()
    if part_numbers_to_match:
        part_number_related_codes = PartCode.objects.filter(
            part_number__in=part_numbers_to_match
        ).exclude(
            pk__in=[pc.pk for pc in basic_part_codes]
        )

    # Get parts used in maintenance history
    parts_used_in_history = []
    for record in maintenance_records:
        parts_used_in_history.extend(record.maintenancepart_set.all())
    
    context = {
        'valve': valve,
        'maintenance_records': maintenance_records,
        'basic_part_codes': basic_part_codes,
        'part_number_related_codes': part_number_related_codes,
        'parts_used_in_history': parts_used_in_history,
        'selected_part_number': selected_part_number,
    }
    return render(request, 'valves/valve_detail.html', context)

@login_required
def valve_create_frontend(request):
    """
    Handle creation of a new valve through the frontend interface.
    GET: Display the valve creation form
    POST: Process the submitted form and create a new valve
    """
    # Get redirect URL from query param or referer
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER', '')
    valve_list_url = reverse('valves:valve-list-frontend')

    if request.method == 'POST':
        post_next = request.POST.get('next')
        # Extract form data
        tag_number = request.POST.get('tag_number')
        name = request.POST.get('name')
        valve_type_id = request.POST.get('valve_type')
        status_id = request.POST.get('status')
        manufacturer_id = request.POST.get('manufacturer')
        factory_id = request.POST.get('factory')
        location = request.POST.get('location')
        installation_date = request.POST.get('installation_date') or None
        last_maintenance_date = request.POST.get('last_maintenance_date') or None
        drawing_link = request.POST.get('drawing_link')
        model_number = request.POST.get('model_number')
        shut_off_pressure = request.POST.get('shut_off_pressure')
        power_failure_pos = request.POST.get('power_failure_pos')
        body_style = request.POST.get('body_style')
        required_travel_angle = request.POST.get('required_travel_angle')
        bench_range = request.POST.get('bench_range')
        plug_stem_mat = request.POST.get('plug_stem_mat')
        butterfly_shaft_mat = request.POST.get('butterfly_shaft_mat')
        seat_guide_mat = request.POST.get('seat_guide_mat')
        seat_diameter = request.POST.get('seat_diameter')
        trim_coating = request.POST.get('trim_coating')
        leakage_class = request.POST.get('leakage_class')
        packing_mat = request.POST.get('packing_mat')
        notes = request.POST.get('notes')

        try:
            # Create new valve object
            valve = Valve.objects.create(
                tag_number=tag_number,
                name=name,
                valve_type_id=valve_type_id,
                status_id=status_id,
                manufacturer_id=manufacturer_id,
                factory_id=factory_id,
                location=location,
                installation_date=installation_date,
                last_maintenance_date=last_maintenance_date,
                drawing_link=drawing_link,
                model_number=model_number,
                shut_off_pressure=shut_off_pressure,
                power_failure_pos=power_failure_pos,
                body_style=body_style,
                required_travel_angle=required_travel_angle,
                bench_range=bench_range,
                plug_stem_mat=plug_stem_mat,
                butterfly_shaft_mat=butterfly_shaft_mat,
                seat_guide_mat=seat_guide_mat,
                seat_diameter=seat_diameter,
                trim_coating=trim_coating,
                leakage_class=leakage_class,
                packing_mat=packing_mat,
                notes=notes
            )
            messages.success(request, f'Valve {valve.tag_number} was created successfully.')
            
            if post_next:
                return HttpResponseRedirect(post_next)
            return redirect('valves:valve-detail-frontend', pk=valve.pk)
        except Exception as e:
            messages.error(request, f'Error creating valve: {str(e)}')
            next_url = post_next

    # For GET requests, prepare the form context
    context = {
        'valve_types': ValveType.objects.all().order_by('name'),
        'statuses': ValveStatus.objects.all().order_by('name'),
        'manufacturers': Manufacturer.objects.all().order_by('name'),
        'factories': Factory.objects.all().order_by('name'),
        'next_url': next_url,
        'valve_list_url': valve_list_url,
        'title': "Create New Valve",
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
        factories = Factory.objects.all().order_by('name')
        main_factories = []
        zld_factory = None

        for factory in factories:
            factory_valves = Valve.objects.filter(factory=factory)
            factory.total_valves = factory_valves.count()
            # Status matching should be robust
            factory.operational_valves = factory_valves.filter(status__name__icontains='Operational').count()
            factory.needs_maintenance_valves = factory_valves.filter(status__name__icontains='Needs Maintenance').count()

            if factory.name == 'ZLD':
                zld_factory = factory
            else:
                # Add factory to list
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

    # Get redirect URL from query param or referer
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER', '')

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
        post_next = request.POST.get('next')
        if form.is_valid():
            instance = form.save()
            messages.success(request, "Maintenance record saved successfully!")

            # If we have a 'next' URL from the form, use it
            if post_next:
                return HttpResponseRedirect(post_next)

            # Default fallback
            redirect_url = reverse('valves:valve-detail-frontend', kwargs={'pk': instance.valve.pk})
            return HttpResponseRedirect(redirect_url + '#maintenance-pane')
        else:
            messages.error(request, "Please correct the errors below.")
            next_url = post_next # Preserve next_url on form error
    else:
        form = MaintenanceHistoryForm(instance=record, initial=initial_data)

    title = "Update Maintenance Record" if pk else "Create New Maintenance Record"
    
    # Sensible default fallback if next_url is missing
    if valve_instance:
        default_back_url = reverse('valves:valve-detail-frontend', kwargs={'pk': valve_instance.pk}) + '#maintenance-pane'
    else:
        default_back_url = reverse('valves:maintenance-history-frontend')

    context = {
        'form': form,
        'title': title,
        'pk': pk,
        'valve': valve_instance,
        'technicians': technicians,
        'next_url': next_url,
        'default_back_url': default_back_url
    }
    return render(request, 'valves/maintenance_form.html', context)

@login_required
def valve_update_frontend(request, pk):
    """
    Handle updating an existing valve through the frontend interface.
    """
    valve = get_object_or_404(Valve, pk=pk)

    # Get redirect URL
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER', '')

    if request.method == 'POST':
        post_next = request.POST.get('next')
        try:
            # Update valve data
            valve.tag_number = request.POST.get('tag_number')
            valve.name = request.POST.get('name')
            valve.valve_type_id = request.POST.get('valve_type')
            valve.status_id = request.POST.get('status')
            valve.manufacturer_id = request.POST.get('manufacturer')
            valve.factory_id = request.POST.get('factory')
            valve.location = request.POST.get('location')
            valve.installation_date = request.POST.get('installation_date') or None
            valve.last_maintenance_date = request.POST.get('last_maintenance_date') or None
            valve.drawing_link = request.POST.get('drawing_link')
            valve.model_number = request.POST.get('model_number')
            valve.shut_off_pressure = request.POST.get('shut_off_pressure')
            valve.power_failure_pos = request.POST.get('power_failure_pos')
            valve.body_style = request.POST.get('body_style')
            valve.required_travel_angle = request.POST.get('required_travel_angle')
            valve.bench_range = request.POST.get('bench_range')
            valve.plug_stem_mat = request.POST.get('plug_stem_mat')
            valve.butterfly_shaft_mat = request.POST.get('butterfly_shaft_mat')
            valve.seat_guide_mat = request.POST.get('seat_guide_mat')
            valve.seat_diameter = request.POST.get('seat_diameter')
            valve.trim_coating = request.POST.get('trim_coating')
            valve.leakage_class = request.POST.get('leakage_class')
            valve.packing_mat = request.POST.get('packing_mat')
            valve.notes = request.POST.get('notes')
            valve.save()

            messages.success(request, f'Valve {valve.tag_number} was updated successfully.')

            if post_next:
                return HttpResponseRedirect(post_next)
            return redirect('valves:valve-detail-frontend', pk=valve.pk)
        except Exception as e:
            messages.error(request, f'Error updating valve: {str(e)}')
            next_url = post_next

    context = {
        'valve': valve,
        'valve_types': ValveType.objects.all().order_by('name'),
        'statuses': ValveStatus.objects.all().order_by('name'),
        'manufacturers': Manufacturer.objects.all().order_by('name'),
        'factories': Factory.objects.all().order_by('name'),
        'next_url': next_url,
        'valve_list_url': reverse('valves:valve-list-frontend'),
        'is_update': True,
        'pk': pk,
        'title': f"Update Valve: {valve.tag_number}"
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
        'valve', 'valve__factory', 'valve__valve_type', 'technician'
    ).prefetch_related(
        'maintenancepart_set',
        'maintenancepart_set__code'
    ).order_by('-maintenance_date')

    # Get filter parameters
    search_query = request.GET.get('q', '')
    selected_factory_id = request.GET.get('factory')
    selected_start_date = request.GET.get('start_date')
    selected_end_date = request.GET.get('end_date')

    if search_query:
        maintenance_list = maintenance_list.filter(
            Q(valve__tag_number__icontains=search_query) |
            Q(maintenance_notes__icontains=search_query) |
            Q(maintenance_activities__icontains=search_query) |
            Q(technician__name__icontains=search_query)
        )

    if selected_factory_id:
        maintenance_list = maintenance_list.filter(valve__factory_id=selected_factory_id)
    if selected_start_date:
        maintenance_list = maintenance_list.filter(maintenance_date__gte=selected_start_date)
    if selected_end_date:
        maintenance_list = maintenance_list.filter(maintenance_date__lte=selected_end_date)

    # Pagination
    paginator = Paginator(maintenance_list, 15)
    page_number = request.GET.get('page')
    maintenance_records = paginator.get_page(page_number)

    # Context for filters
    factories = Factory.objects.all().order_by('name')

    context = {
        'maintenance_records': maintenance_records,
        'search_query': search_query,
        'factories': factories,
        'selected_factory_id': selected_factory_id,
        'selected_start_date': selected_start_date,
        'selected_end_date': selected_end_date,
    }
    return render(request, 'valves/maintenance_list.html', context)
@login_required
def maintenance_detail_frontend(request, pk):
    """
    Display detailed information about a specific maintenance record.
    """
    maintenance = get_object_or_404(
        MaintenanceHistory.objects.select_related('valve', 'technician'),
        pk=pk
    )

    parts_used = maintenance.maintenancepart_set.all()

    # Get all selected activities
    all_activities = []
    if maintenance.maintenance_activities:
        all_activities = [a.strip() for a in maintenance.maintenance_activities.split(',') if a.strip()]

    # Identify activities that are already linked to a part
    linked_activity_names = [p.associated_activity for p in parts_used if p.associated_activity]

    # Only keep activities that are NOT linked to a part (to avoid double rows)
    unlinked_activities = [a for a in all_activities if a not in linked_activity_names]

    context = {
        'record': maintenance,
        'parts_used': parts_used,
        'activities': unlinked_activities,
        'MAINTENANCE_LIST_URL': reverse('valves:maintenance-history-frontend'),
        'title': f"Maintenance Record - {maintenance.valve.tag_number}",
    }
    return render(request, 'valves/maintenance_detail.html', context)
@login_required
def part_code_list_frontend(request):
    """
    Display list of all part codes with filtering and pagination.
    """
    part_codes_list = PartCode.objects.all().order_by('sap_code')
    
    search_query = request.GET.get('q', '')
    part_number_filter = request.GET.get('part_number', '')

    if part_number_filter:
        part_codes_list = part_codes_list.filter(part_number=part_number_filter)
    elif search_query:
        part_codes_list = part_codes_list.filter(
            Q(sap_code__icontains=search_query) |
            Q(oracle_code__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(part_number__icontains=search_query)
        )
    
    paginator = Paginator(part_codes_list, 15)
    page_number = request.GET.get('page')
    part_codes = paginator.get_page(page_number)
    
    context = {
        'part_codes': part_codes,
        'search_query': search_query,
        'part_number_filter': part_number_filter,
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
        'valves': part_code.associated_valves.all(),
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

from django.http import JsonResponse
from django.views.decorators.http import require_GET

@login_required
def valve_tag_autocomplete(request):
    if 'term' in request.GET:
        qs = Valve.objects.filter(tag_number__icontains=request.GET.get('term'))
        tags = [valve.tag_number for valve in qs]
        return JsonResponse(tags, safe=False)
    return JsonResponse([], safe=False)

@login_required
@require_GET
def get_valves_by_factory(request):
    """
    API endpoint to get valves by factory, with optional search.
    """
    factory_id = request.GET.get('factory')
    search_term = request.GET.get('q', '')

    if not factory_id:
        return JsonResponse({'error': 'Factory ID is required'}, status=400)
    
    try:
        valves = Valve.objects.filter(factory_id=factory_id)
        if search_term:
            valves = valves.filter(tag_number__icontains=search_term)
        
        valves = valves.values('valve_id', 'tag_number')
        return JsonResponse(list(valves), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def shutdown_report(request):
    """
    Handle creation and display of shutdown reports, focusing ONLY on shutdown records.
    """
    # Only show records marked as is_shutdown=True
    maintenance_records_list = MaintenanceHistory.objects.filter(is_shutdown=True).select_related(
        'valve', 'valve__factory', 'technician'
    ).prefetch_related('maintenancepart_set__part_code')

    selected_factory = request.GET.get('factory')
    selected_period = request.GET.get('period')

    # Apply filters
    if selected_factory:
        maintenance_records_list = maintenance_records_list.filter(valve__factory__name=selected_factory)

    if selected_period:
        maintenance_records_list = maintenance_records_list.filter(
            valve__shutdown__name=selected_period
        ).distinct()

    maintenance_records_list = maintenance_records_list.order_by('-maintenance_date')

    # Pagination
    paginator = Paginator(maintenance_records_list, 15)
    page_number = request.GET.get('page')
    maintenance_records = paginator.get_page(page_number)

    # Get distinct shutdown names (Months/Years) for the period dropdown
    periods = Shutdown.objects.values_list('name', flat=True).distinct().order_by('-start_date')

    context = {
        'maintenance_records': maintenance_records,
        'periods': periods,
        'selected_factory': selected_factory,
        'selected_period': selected_period,
    }
    return render(request, 'valves/shutdown_report.html', context)


@login_required

def shutdown_report_print(request, pk):

    """

    Generate printable version of a specific shutdown report.

    """

    shutdown = get_object_or_404(Shutdown, pk=pk)

    

    context = {

        'shutdowns': [shutdown],

        'print_mode': True

    }

    return render(request, 'valves/shutdown_report_print.html', context)





import os





from django.conf import settings





from django.core.files.storage import default_storage





from .forms import DocumentUploadForm











@login_required











def documents_page(request):











    """











    Display a list of documents and folders from the media directory











    and handle file uploads.











    """











    if request.method == 'POST':











        form = DocumentUploadForm(request.POST, request.FILES)











        if form.is_valid():











            factory = form.cleaned_data['factory']











            document_type = form.cleaned_data['document_type']











            name = form.cleaned_data['name']











            uploaded_file = form.cleaned_data['file']











            











            # Get the file extension











            file_extension = os.path.splitext(uploaded_file.name)[1]











            











            # Construct the path











            upload_dir = os.path.join(settings.MEDIA_ROOT, factory, document_type)











            os.makedirs(upload_dir, exist_ok=True)











            











            file_path = os.path.join(upload_dir, f"{name}{file_extension}")











            











            # Save the file











            default_storage.save(file_path, uploaded_file)











            











            messages.success(request, f"File '{name}{file_extension}' uploaded successfully to {factory}/{document_type}.")











            return redirect('valves:documents-page')











        else:











            messages.error(request, "There was an error with your upload. Please check the form.")











    else:











        form = DocumentUploadForm()























    media_path = settings.MEDIA_ROOT











    documents_structure = {}











    











    if os.path.exists(media_path):











        for factory_dir in os.listdir(media_path):











            if factory_dir.lower() == 'valves':











                continue











            factory_path = os.path.join(media_path, factory_dir)











            if os.path.isdir(factory_path):











                documents_structure[factory_dir] = {}











                for doc_type_dir in os.listdir(factory_path):











                    doc_type_path = os.path.join(factory_path, doc_type_dir)











                    if os.path.isdir(doc_type_path):











                        documents_structure[factory_dir][doc_type_dir] = []











                        # Recursive search using os.walk











                        for root, _, files in os.walk(doc_type_path):











                            for filename in files:











                                file_path = os.path.join(root, filename)











                                











                                # Get relative path from doc_type_path for display name











                                relative_name = os.path.relpath(file_path, doc_type_path).replace("\\", "/")























                                # Get relative path from media_path for URL











                                relative_url_path = os.path.relpath(file_path, media_path).replace("\\", "/")











                                media_url = os.path.join(settings.MEDIA_URL, relative_url_path).replace("\\", "/")























                                documents_structure[factory_dir][doc_type_dir].append({











                                    'name': relative_name,











                                    'path': media_url











                                })























    context = {











        'documents': documents_structure,











        'upload_form': form,











    }











    return render(request, 'valves/documents.html', context)


# ==========================================
# Backup & Restore Enterprise Views
# ==========================================

from django.http import FileResponse, Http404
import backup_manager


def backup_management_view(request):
    """Enterprise Backup & Restore Management Dashboard."""
    engine = backup_manager.get_backup_engine()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            note = request.POST.get('note', 'Manual snapshot from Web/Desktop UI')
            res = engine.create_backup(backup_type='manual', note=note)
            if res.get('success'):
                messages.success(request, f"Backup successfully created: {res.get('filename')} (SHA: {res.get('checksum')[:12]}...)")
            else:
                messages.error(request, f"Failed to create backup: {res.get('error')}")
            return redirect('valves:backup-management')

        elif action == 'restore':
            filename = request.POST.get('filename')
            if filename:
                archive_path = engine.backup_dir / filename
                res = engine.restore_backup(archive_path)
                if res.get('success'):
                    messages.success(request, f"System successfully restored from {filename}. Pre-restore safety snapshot created: {res.get('safety_backup')}.")
                else:
                    messages.error(request, f"Restore failed: {res.get('error')}")
            elif 'backup_file' in request.FILES:
                uploaded = request.FILES['backup_file']
                upload_path = engine.backup_dir / f"uploaded_{uploaded.name}"
                with open(upload_path, 'wb+') as dest:
                    for chunk in uploaded.chunks():
                        dest.write(chunk)
                res = engine.restore_backup(upload_path)
                if res.get('success'):
                    messages.success(request, f"System successfully restored from uploaded archive: {uploaded.name}.")
                else:
                    messages.error(request, f"Restore failed: {res.get('error')}")
            return redirect('valves:backup-management')

        elif action == 'verify':
            filename = request.POST.get('filename')
            if filename:
                archive_path = engine.backup_dir / filename
                res = engine.verify_backup(archive_path)
                if res.get('valid'):
                    messages.success(request, f"Integrity Verified: {filename} matches SHA-256 and has zero corruption.")
                else:
                    messages.error(request, f"Verification Failed for {filename}: {res.get('error')}")
            return redirect('valves:backup-management')

    backups = engine.list_backups()
    context = {
        'backups': backups,
        'retention_limits': engine.RETENTION_LIMITS,
        'backup_dir': str(engine.backup_dir),
        'db_path': str(engine.db_path),
        'total_backups_count': len(backups),
        'total_size_mb': round(sum(b.get('size_mb', 0) for b in backups), 2),
    }
    return render(request, 'valves/backup_management.html', context)


def backup_download_view(request, filename):
    """Secure point-in-time backup archive export."""
    engine = backup_manager.get_backup_engine()
    target_path = engine.backup_dir / filename

    try:
        target_path = target_path.resolve()
        if not str(target_path).startswith(str(engine.backup_dir.resolve())):
            raise Http404("Invalid file path.")
    except Exception:
        raise Http404("Invalid file path.")

    if not target_path.exists():
        raise Http404("Backup file not found.")

    return FileResponse(open(target_path, 'rb'), as_attachment=True, filename=filename)


# ==========================================
# User Management & Access Control Views
# ==========================================

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry
from .models import UserProfile, Factory, Technician
from .forms import UserCreateForm, UserUpdateForm


def admin_required(view_func):
    """Decorator ensuring only system administrators can access user management."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('valves:login')
        is_admin = request.user.is_superuser or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_admin:
            messages.error(request, "عذراً، هذه الخاصية مخصصة لمدير النظام (Admin) فقط.")
            return redirect('valves:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def user_list_view(request):
    """Dashboard to manage and inspect all users and their assignments."""
    users = list(User.objects.all().select_related('profile', 'profile__factory', 'profile__technician').order_by('-is_superuser', '-is_active', 'username'))

    # Auto-ensure profile for any user
    for u in users:
        if not hasattr(u, 'profile'):
            role = 'admin' if u.is_superuser else ('supervisor' if u.is_staff else 'technician')
            UserProfile.objects.create(user=u, role=role)

    # Attach stats
    for u in users:
        u.maintenance_count = 0
        if hasattr(u, 'profile') and u.profile.technician:
            u.maintenance_count = MaintenanceHistory.objects.filter(technician=u.profile.technician).count()
        u.recent_actions_count = LogEntry.objects.filter(user=u).count()

    total_users = len(users)
    active_users = sum(1 for u in users if u.is_active)
    admins_count = sum(1 for u in users if u.is_superuser or (hasattr(u, 'profile') and u.profile.role == 'admin'))
    technicians_count = sum(1 for u in users if hasattr(u, 'profile') and u.profile.role == 'technician')

    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'admins_count': admins_count,
        'technicians_count': technicians_count,
    }
    return render(request, 'valves/user_list.html', context)


@admin_required
def user_create_view(request):
    """Add a new user and assign roles and assignments."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            email = form.cleaned_data.get('email', '')
            role = form.cleaned_data['role']
            factory = form.cleaned_data.get('factory')
            technician = form.cleaned_data.get('technician')
            phone_number = form.cleaned_data.get('phone_number', '')
            notes = form.cleaned_data.get('notes', '')
            is_active = form.cleaned_data.get('is_active', True)

            is_superuser = (role == 'admin')
            is_staff = (role in ['admin', 'supervisor'])

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
                is_staff=is_staff,
                is_superuser=is_superuser,
            )

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.factory = factory
            profile.technician = technician
            profile.phone_number = phone_number
            profile.notes = notes
            profile.save()

            messages.success(request, f"تم بنجاح إضافة المستخدم: {username} ({profile.get_role_display()})")
            return redirect('valves:user-list')
    else:
        form = UserCreateForm()

    return render(request, 'valves/user_form.html', {'form': form, 'title': 'إضافة مستخدم جديد للنظام'})


@admin_required
def user_detail_view(request, pk):
    """Inspect user assignments, role, permissions, and operational history."""
    target_user = get_object_or_404(User.objects.select_related('profile', 'profile__factory', 'profile__technician'), pk=pk)

    if not hasattr(target_user, 'profile'):
        role = 'admin' if target_user.is_superuser else ('supervisor' if target_user.is_staff else 'technician')
        profile = UserProfile.objects.create(user=target_user, role=role)
    else:
        profile = target_user.profile

    # Fetch technician maintenance records if linked
    maintenance_records = []
    if profile.technician:
        maintenance_records = MaintenanceHistory.objects.filter(technician=profile.technician).select_related('valve', 'technician').order_by('-maintenance_date')[:30]

    # Fetch audit log entries
    audit_logs = LogEntry.objects.filter(user=target_user).select_related('content_type').order_by('-action_time')[:30]

    context = {
        'target_user': target_user,
        'profile': profile,
        'maintenance_records': maintenance_records,
        'audit_logs': audit_logs,
        'permissions_list': profile.permissions_summary,
    }
    return render(request, 'valves/user_detail.html', context)


@admin_required
def user_update_view(request, pk):
    """Edit user details, roles, permissions, and password."""
    target_user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(
        user=target_user,
        defaults={'role': 'admin' if target_user.is_superuser else 'technician'}
    )

    if request.method == 'POST':
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            target_user.first_name = form.cleaned_data.get('first_name', '')
            target_user.last_name = form.cleaned_data.get('last_name', '')
            target_user.email = form.cleaned_data.get('email', '')
            target_user.is_active = form.cleaned_data.get('is_active', True)

            new_password = form.cleaned_data.get('new_password')
            if new_password:
                target_user.set_password(new_password)

            role = form.cleaned_data['role']
            target_user.is_superuser = (role == 'admin')
            target_user.is_staff = (role in ['admin', 'supervisor'])
            target_user.save()

            profile.role = role
            profile.factory = form.cleaned_data.get('factory')
            profile.technician = form.cleaned_data.get('technician')
            profile.phone_number = form.cleaned_data.get('phone_number', '')
            profile.notes = form.cleaned_data.get('notes', '')
            profile.save()

            messages.success(request, f"تم بنجاح تحديث بيانات وتكليفات المستخدم: {target_user.username}")
            return redirect('valves:user-detail', pk=pk)
    else:
        form = UserUpdateForm(initial={
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_user.email,
            'role': profile.role,
            'factory': profile.factory,
            'technician': profile.technician,
            'phone_number': profile.phone_number,
            'notes': profile.notes,
            'is_active': target_user.is_active,
        })

    return render(request, 'valves/user_form.html', {
        'form': form,
        'title': f'تعديل بيانات المستخدم: {target_user.username}',
        'target_user': target_user,
    })


@admin_required
def user_delete_view(request, pk):
    """Safely delete user with validation against deleting self or last admin."""
    target_user = get_object_or_404(User, pk=pk)

    if request.user.pk == target_user.pk:
        messages.error(request, "لا يمكنك حذف حسابك الشخصي الذي تستخدمه حالياً!")
        return redirect('valves:user-list')

    if target_user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
        messages.error(request, "لا يمكن حذف آخر مدير نظام (Superuser) في المنظومة!")
        return redirect('valves:user-list')

    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f"تم حذف المستخدم ({username}) بنجاح.")
        return redirect('valves:user-list')

    return render(request, 'valves/user_confirm_delete.html', {'target_user': target_user})


@admin_required
def user_toggle_status_view(request, pk):
    """Toggle user active / disabled status."""
    target_user = get_object_or_404(User, pk=pk)

    if request.user.pk == target_user.pk:
        messages.error(request, "لا يمكنك تعطيل حسابك الشخصي!")
        return redirect('valves:user-list')

    target_user.is_active = not target_user.is_active
    target_user.save()
    status_str = "تفعيل" if target_user.is_active else "تعطيل"
    messages.success(request, f"تم {status_str} حساب المستخدم ({target_user.username}) بنجاح.")
    return redirect('valves:user-list')








