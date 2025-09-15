from django import forms
from .models import Valve

class ValveForm(forms.ModelForm):
    class Meta:
        model = Valve
        fields = '__all__' # ده بيخلي الفورم ياخد كل الحقول من الـ Model
        # لو عايز تختار حقول معينة بس، ممكن تعمل كده:
        # fields = ['tag_number', 'name', 'location', 'valve_type', 'status', 'installation_date', 'last_maintenance_date', 'notes']

        widgets = {
            'tag_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'valve_type': forms.Select(attrs={'class': 'form-control'}), # لو عندك اختيارات هتظهر dropdown
            'status': forms.Select(attrs={'class': 'form-control'}),     # لو عندك اختيارات هتظهر dropdown
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

        labels = {
            'tag_number': 'الرقم التعريفي للبلف',
            'name': 'الاسم',
            'location': 'الموقع',
            'valve_type': 'النوع',
            'status': 'الحالة',
            'installation_date': 'تاريخ التثبيت',
            'last_maintenance_date': 'آخر صيانة',
            'notes': 'ملاحظات',
        }