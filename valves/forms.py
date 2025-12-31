from django import forms
from .models import Valve, SparePart, PartCode, MaintenanceHistory, Shutdown, Technician

class ValveForm(forms.ModelForm):
    class Meta:
        model = Valve
        fields = '__all__'
        widgets = {
            'tag_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'valve_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'drawing_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link to engineering drawing file'}),
        }
        labels = {
            'tag_number': 'Valve Tag Number',
            'name': 'Name',
            'location': 'Location',
            'valve_type': 'Type',
            'status': 'Status',
            'installation_date': 'Installation Date',
            'last_maintenance_date': 'Last Maintenance',
            'notes': 'Notes',
            'drawing_link': 'Engineering Drawing Link',
        }

class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = '__all__'
        widgets = {
            'part_id': forms.TextInput(attrs={'class': 'form-control'}),
            'part_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'part_id': 'Part ID',
            'part_name': 'Part Name',
        }

class PartCodeForm(forms.ModelForm):
    class Meta:
        model = PartCode
        fields = '__all__'
        widgets = {
            'code_id': forms.TextInput(attrs={'class': 'form-control'}),
            'part': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'code_id': 'Code ID',
            'part': 'Main Spare Part',
            'description': 'Detailed description of the code',
            'quantity': 'Available quantity',
            'unit_price': 'Unit price',
            'location': 'Location in warehouse',
            'category': 'Category',
        }

class MaintenanceHistoryForm(forms.ModelForm):
    valve_tag_number = forms.CharField(
        label='Valve Tag Number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start typing to search for a valve...'}),
        required=True
    )
    technician_name = forms.CharField(
        label='Technician/supervisor name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name...', 'list': 'technicians-list'}),
        required=True
    )
    maintenance_activities = forms.MultipleChoiceField(
        choices=[
            ('On site', 'On site'),
            ('In the workshop', 'In the workshop'),
            ('Gland tightening', 'Gland tightening'),
            ('Adding packing', 'Adding packing'),
            ('Replacing packing', 'Replacing packing'),
            ('Replacing actuator', 'Replacing actuator'),
            ('Replacing bushing', 'Replacing bushing'),
            ('Replacing diaphragm', 'Replacing diaphragm'),
            ('Replacing plug', 'Replacing plug'),
            ('Machining plug', 'Machining plug'),
            ('Replacing seat', 'Replacing seat'),
            ('Machining seat', 'Machining seat'),
            ('Replacing cage', 'Replacing cage'),
            ('Machining cage', 'Machining cage'),
            ('Welding plug', 'Welding plug'),
            ('Welding seat', 'Welding seat'),
            ('Welding body', 'Welding body'),
            ('Machining body', 'Machining body'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = MaintenanceHistory
        fields = [
            'valve_tag_number', 'valve', 'maintenance_date', 
            'oracle_code', 'maintenance_activities', 'maintenance_notes', 'is_active', 
            'before_image', 'after_image'
        ]
        widgets = {
            'valve': forms.HiddenInput(),
            'maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'oracle_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SAP Code / Oracle Code / Order Number'}),
            'maintenance_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'before_image': forms.FileInput(attrs={'class': 'form-control'}),
            'after_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'valve': 'Valve ID',
            'maintenance_date': 'Actual maintenance date',
            'oracle_code': 'SAP Code / Oracle Code / Order Number',
            'maintenance_notes': 'Detailed maintenance notes',
            'is_active': 'Maintenance record active',
            'before_image': 'Valve image (before maintenance)',
            'after_image': 'Valve image (after maintenance)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valve'].required = False
        if self.instance and self.instance.pk:
            if self.instance.valve:
                self.fields['valve_tag_number'].initial = self.instance.valve.tag_number
            if self.instance.technician:
                self.fields['technician_name'].initial = self.instance.technician.name
            if self.instance.maintenance_activities:
                self.fields['maintenance_activities'].initial = self.instance.maintenance_activities.split(',')

    def clean(self):
        cleaned_data = super().clean()
        valve_tag_number = cleaned_data.get("valve_tag_number")
        if valve_tag_number:
            valve = Valve.objects.filter(tag_number=valve_tag_number).first()
            if valve:
                cleaned_data['valve'] = valve
            else:
                self.add_error('valve_tag_number', "No valve found with this tag number.")
        
        technician_name = cleaned_data.get("technician_name")
        if technician_name:
            technician, _ = Technician.objects.get_or_create(name=technician_name)
            cleaned_data['technician'] = technician
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.technician = self.cleaned_data.get('technician')
        instance.valve = self.cleaned_data.get('valve')
        instance.maintenance_activities = ','.join(self.cleaned_data.get('maintenance_activities', []))
        
        if commit:
            instance.save()
        return instance

class ShutdownReportForm(forms.ModelForm):
    valves = forms.ModelMultipleChoiceField(
        queryset=Valve.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2-multiple', 'multiple': 'multiple'}),
        required=False
    )

    class Meta:
        model = Shutdown
        fields = ['factory', 'start_date', 'end_date', 'valves']
        widgets = {
            'factory': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valves'].queryset = Valve.objects.none()
        self.fields['valves'].widget.attrs['disabled'] = 'disabled'

        if 'factory' in self.data:
            try:
                factory_id = int(self.data.get('factory'))
                self.fields['valves'].queryset = Valve.objects.filter(factory_id=factory_id).order_by('tag_number')
                self.fields['valves'].widget.attrs.pop('disabled')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.factory:
            self.fields['valves'].queryset = self.instance.factory.valve_set.order_by('tag_number')
            self.fields['valves'].widget.attrs.pop('disabled')

class DocumentUploadForm(forms.Form):
    factory = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'factory-list'}))
    document_type = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'doctype-list'}))
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
        