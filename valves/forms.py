import calendar
from datetime import date
from django import forms
from django.db.models import Q
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart, Shutdown, Technician

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
            'plug_stem_mat': forms.TextInput(attrs={'class': 'form-control'}),
            'butterfly_shaft_mat': forms.TextInput(attrs={'class': 'form-control'}),
            'seat_guide_mat': forms.TextInput(attrs={'class': 'form-control'}),
            'seat_diameter': forms.TextInput(attrs={'class': 'form-control'}),
            'trim_coating': forms.TextInput(attrs={'class': 'form-control'}),
            'leakage_class': forms.TextInput(attrs={'class': 'form-control'}),
            'packing_mat': forms.TextInput(attrs={'class': 'form-control'}),
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
            'plug_stem_mat': 'Plug/Stem MAT',
            'butterfly_shaft_mat': 'Butterfly/Shaft MAT',
            'seat_guide_mat': 'Seat/Guide MAT',
            'seat_diameter': 'Seat Diameter',
            'trim_coating': 'Trim Coating',
            'leakage_class': 'Leakage Class',
            'packing_mat': 'Packing MAT',
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

    is_shutdown = forms.BooleanField(
        label='Shutdown',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = MaintenanceHistory
        fields = [
            'valve_tag_number', 'valve', 'is_shutdown', 'maintenance_date', 
            'oracle_code', 'maintenance_activities', 'maintenance_notes',
            'pressure_test', 'testing_pressure', 'is_active', 
            'before_image', 'after_image'
        ]
        widgets = {
            'valve': forms.HiddenInput(),
            'maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'oracle_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SAP Code / Oracle Code / Order Number'}),
            'maintenance_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'pressure_test': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Pass/Fail, Seat Leakage...'}),
            'testing_pressure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Pressure in Bar'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'before_image': forms.FileInput(attrs={'class': 'form-control'}),
            'after_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'valve': 'Valve ID',
            'maintenance_date': 'Actual maintenance date',
            'oracle_code': 'SAP Code / Oracle Code / Order Number',
            'maintenance_notes': 'Detailed maintenance notes',
            'pressure_test': 'Pressure Test Result',
            'testing_pressure': 'Testing Pressure (Bar)',
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
            # Ensure is_shutdown is explicitly initialized
            self.fields['is_shutdown'].initial = self.instance.is_shutdown

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
        instance.is_shutdown = self.cleaned_data.get('is_shutdown', False)
        instance.maintenance_activities = ','.join(self.cleaned_data.get('maintenance_activities', []))
        
        if commit:
            instance.save()
            
            # Process activity-specific codes
            choices = self.fields['maintenance_activities'].choices
            for key, value in self.data.items():
                if key.startswith('activity_code_') and value:
                    try:
                        # Extract the index from activity_code_1, activity_code_2, etc.
                        idx = int(key.split('_')[-1]) - 1
                        activity_name = choices[idx][0]
                        
                        # Look up the part code
                        part_code = PartCode.objects.filter(
                            Q(sap_code=value) | 
                            Q(oracle_code=value) | 
                            Q(part_number=value)
                        ).first()
                        
                        if part_code and part_code.part:
                            MaintenancePart.objects.get_or_create(
                                maintenance_event=instance,
                                part=part_code.part,
                                code=part_code,
                                associated_activity=activity_name,
                                entered_code=value,
                                defaults={'quantity_used': 1.0}
                            )
                        else:
                            # Create a record even if part is not found in database
                            MaintenancePart.objects.get_or_create(
                                maintenance_event=instance,
                                associated_activity=activity_name,
                                entered_code=value,
                                defaults={'quantity_used': 1.0}
                            )
                    except (ValueError, IndexError):
                        continue
            
            # Also check the global oracle_code field if it has a value
            oracle_code = self.cleaned_data.get('oracle_code')
            if oracle_code:
                part_code = PartCode.objects.filter(
                    Q(sap_code=oracle_code) | 
                    Q(oracle_code=oracle_code) | 
                    Q(part_number=oracle_code)
                ).first()
                
                if part_code and part_code.part:
                    MaintenancePart.objects.get_or_create(
                        maintenance_event=instance,
                        part=part_code.part,
                        code=part_code,
                        entered_code=oracle_code,
                        defaults={'quantity_used': 1.0}
                    )
                else:
                    MaintenancePart.objects.get_or_create(
                        maintenance_event=instance,
                        entered_code=oracle_code,
                        defaults={'quantity_used': 1.0}
                    )

            # --- New Shutdown Logic ---
            if instance.is_shutdown and instance.valve and instance.valve.factory:
                m_date = instance.maintenance_date
                if m_date:
                    # Create a name like "January 2026"
                    shutdown_name = m_date.strftime("%B %Y")
                    
                    # Determine start and end of month
                    last_day = calendar.monthrange(m_date.year, m_date.month)[1]
                    start_dt = date(m_date.year, m_date.month, 1)
                    end_dt = date(m_date.year, m_date.month, last_day)
                    
                    # Ensure Shutdown object exists for this factory and month
                    shutdown, created = Shutdown.objects.get_or_create(
                        name=shutdown_name,
                        factory=instance.valve.factory,
                        defaults={
                            'start_date': start_dt,
                            'end_date': end_dt
                        }
                    )
                    # If it already existed but with wrong dates (unlikely), update them
                    if not created:
                        shutdown.start_date = start_dt
                        shutdown.end_date = end_dt
                        shutdown.save()
                        
                    # Add this valve to the shutdown list
                    shutdown.valves.add(instance.valve)
            # --------------------------

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


from django.contrib.auth.models import User
from .models import UserProfile, Factory, Technician


class UserCreateForm(forms.Form):
    username = forms.CharField(
        label="اسم المستخدم (Username)",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ahmed_tech'})
    )
    first_name = forms.CharField(
        label="الاسم الأول",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. أحمد'})
    )
    last_name = forms.CharField(
        label="اسم العائلة",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. علي'})
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ahmed@company.com'})
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="يجب ألا تقل عن 6 خانات"
    )
    confirm_password = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label="الدور والصلاحيات داخل المنظومة",
        choices=UserProfile.ROLE_CHOICES,
        initial='technician',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    factory = forms.ModelChoiceField(
        label="المصنع المكلف به (اختياري)",
        queryset=Factory.objects.all(),
        required=False,
        empty_label="-- جميع المصانع / بدون تخصيص --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    technician = forms.ModelChoiceField(
        label="فني الصيانة المرتبط (اختياري)",
        queryset=Technician.objects.all().order_by('name'),
        required=False,
        empty_label="-- بدون ربط بسجل فني --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone_number = forms.CharField(
        label="رقم الهاتف (اختياري)",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01xxxxxxxxx'})
    )
    can_export = forms.BooleanField(
        label="صلاحية تصدير البيانات (Excel/CSV)",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    can_import = forms.BooleanField(
        label="صلاحية استيراد وتحديث البيانات (Excel/CSV)",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        label="ملاحظات وتكليفات خاصة",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    is_active = forms.BooleanField(
        label="الحساب مفعل ويمكنه تسجيل الدخول",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("اسم المستخدم هذا مستخدم بالفعل، يرجى اختيار اسم آخر.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "كلمات المرور غير متطابقة.")
            if len(password) < 6:
                self.add_error('password', "كلمة المرور يجب أن تكون 6 خانات على الأقل.")
        return cleaned_data


class UserUpdateForm(forms.Form):
    first_name = forms.CharField(
        label="الاسم الأول",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="اسم العائلة",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        label="تعيين كلمة مرور جديدة",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="اتركه فارغاً إذا كنت لا ترغب بتغيير كلمة المرور الحالية"
    )
    role = forms.ChoiceField(
        label="الدور والصلاحيات داخل المنظومة",
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    factory = forms.ModelChoiceField(
        label="المصنع المكلف به (اختياري)",
        queryset=Factory.objects.all(),
        required=False,
        empty_label="-- جميع المصانع / بدون تخصيص --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    technician = forms.ModelChoiceField(
        label="فني الصيانة المرتبط (اختياري)",
        queryset=Technician.objects.all().order_by('name'),
        required=False,
        empty_label="-- بدون ربط بسجل فني --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone_number = forms.CharField(
        label="رقم الهاتف (اختياري)",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    can_export = forms.BooleanField(
        label="صلاحية تصدير البيانات (Excel/CSV)",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    can_import = forms.BooleanField(
        label="صلاحية استيراد وتحديث البيانات (Excel/CSV)",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        label="ملاحظات وتكليفات خاصة",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    is_active = forms.BooleanField(
        label="الحساب مفعل ويمكنه تسجيل الدخول",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password and len(new_password) < 6:
            raise forms.ValidationError("كلمة المرور الجديدة يجب ألا تقل عن 6 خانات.")
        return new_password

        