from .forms import ValveForm # استيراد الفورم الجديد
from django.contrib import messages # عشان نظهر رسائل للمستخدم
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework import generics
from .models import Valve, SparePart, PartCode, MaintenanceHistory, MaintenancePart
from .serializers import ValveSerializer, SparePartSerializer, PartCodeSerializer, MaintenanceHistorySerializer, MaintenancePartSerializer
import requests
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



@login_required
def home(request):
    return render(request, 'valves/home.html')
@login_required
def valve_list_frontend(request):
      # هنا هنجلب البيانات من الـ API الخاص بينا
    api_url = request.build_absolute_uri('/api/valves/') # بناء رابط الـ API بشكل صحيح
    try:
        response = requests.get(api_url)
        response.raise_for_status() # عشان يرمي استثناء لو فيه خطأ في الرد (4xx أو 5xx)
        valves_data = response.json() # تحويل الرد إلى JSON
    except requests.exceptions.RequestException as e:
        messages.error(request, f'حدث خطأ أثناء جلب بيانات البلوف: {e}')
        valves_data = [] # لو فيه خطأ، نعرض قائمة فارغة

    context = {
        'valves': valves_data # نمرر البيانات للقالب
    }
    return render(request, 'valves/valve_list.html', context)

# @login_required
# def valve_create(request):
#     if request.method == 'POST':
#         form = ValveForm(request.POST)
#         if form.is_valid():
#             form.save() # حفظ البلف الجديد في قاعدة البيانات
#             messages.success(request, 'تمت إضافة البلف بنجاح!') # رسالة نجاح
#             return redirect('valve-list-frontend') # ارجع لقائمة البلوف بعد الحفظ
#         else:
#             messages.error(request, 'حدث خطأ. يرجى مراجعة البيانات المدخلة.') # رسالة خطأ
#     else:
#         form = ValveForm() # لو طلب الصفحة لأول مرة، اعرض فورم فاضي
#     return render(request, 'valves/valve_create.html', {'form': form})

@login_required # لو المستخدم لازم يكون مسجل دخول عشان يشوف التفاصيل
def valve_detail_frontend(request, pk):
    # ده API بتاعك اللي بيجيب بيانات بلف واحد بالـ pk بتاعه
    api_url = f"http://127.0.0.1:8000/api/valves/{pk}/"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # هيرفع HTTPError لو الـ request فشلت
        valve_data = response.json()
        context = {'valve': valve_data}
        return render(request, 'valves/valve_detail.html', context)
    except requests.exceptions.RequestException as e:
        # ممكن تعمل صفحة خطأ مخصصة هنا أو ترجع رسالة بسيطة
        return render(request, 'error_template.html', {'error': f"Error fetching valve details: {e}"})

@login_required
def valve_create_frontend(request):
    error_message = None # متغير جديد لتخزين رسالة الخطأ
    if request.method == 'POST':
        # API URL لإضافة بلف جديد
        api_url = "http://127.0.0.1:8000/api/valves/"
        
        # جمع البيانات من الـ form
        valve_data = {
            'tag_number': request.POST.get('tag_number'),
            'name': request.POST.get('name'),
            'location': request.POST.get('location'),
            'valve_type': request.POST.get('valve_type'),
            'status': request.POST.get('status'),
            'installation_date': request.POST.get('installation_date'),
            'last_maintenance_date': request.POST.get('last_maintenance_date'),
            'notes': request.POST.get('notes'),
            'drawing_link': request.POST.get('drawing_link'),
        }
        try:
            response = requests.post(api_url, data=valve_data)
            response.raise_for_status()  # هيرفع HTTPError لو فيه مشكلة
            return redirect('valve-list-frontend')
        
        except requests.exceptions.HTTPError as err:
            # هنا بنتعامل مع أخطاء الـ API بالتحديد
            if response.status_code == 400:
                try:
                    # بنحاول نجيب رسالة الخطأ من الـ JSON اللي الـ API بيرجعه
                    error_details = response.json()
                    error_message = f"خطأ في البيانات: {error_details}"
                except ValueError:
                    error_message = f"خطأ من الخادم (400): {response.text}"
            else:
                error_message = f"خطأ في HTTP: {err}"
        
        except requests.exceptions.RequestException as e:
            error_message = f"خطأ في الاتصال: {e}"
    
    # بنعرض الـ form تاني وبنبعت معاها رسالة الخطأ
    return render(request, 'valves/valve_create.html', {'error': error_message})
# ... هتضيف الـ view بتاعت التعديل هنا بعدين
@login_required
def valve_update_frontend(request, pk):
    # View فارغة لصفحة التعديل
    # بعدين هنحط هنا كود تعديل بلف
    return render(request, 'valves/valve_update.html') # أو redirect مؤقتاً

@login_required
def maintenance_history_frontend(request):
    api_url = request.build_absolute_uri('/api/maintenance-history/')
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        maintenance_data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f'حدث خطأ أثناء جلب بيانات سجل الصيانة: {e}')
        maintenance_data = []
    context = {
        'maintenance_history': maintenance_data
    }
    return render(request, 'valves/maintenance_history.html', context)

# View لعرض قائمة قطع الغيار
@login_required
def spare_part_list_frontend(request):
    api_url = request.build_absolute_uri('/api/spare-parts/')
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        parts_data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f'حدث خطأ أثناء جلب بيانات قطع الغيار: {e}')
        parts_data = []
    
    context = {
        'spare_parts': parts_data
    }
    return render(request, 'valves/spare_part_list.html', context)

# View لعرض قائمة أكواد قطع الغيار
@login_required
def part_code_list_frontend(request):
    api_url = request.build_absolute_uri('/api/part-codes/')
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        codes_data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f'حدث خطأ أثناء جلب بيانات أكواد القطع: {e}')
        codes_data = []

    context = {
        'part_codes': codes_data
    }
    return render(request, 'valves/part_code_list.html', context)    

@login_required
def valve_delete_frontend(request, pk):
    if request.method == 'POST':
        api_url = request.build_absolute_uri(f'/api/valves/{pk}/')
        try:
            # هنا بنبعت طلب DELETE للـ API عشان يمسح البلف
            response = requests.delete(api_url)
            response.raise_for_status() # عشان نتحقق من نجاح العملية
            messages.success(request, 'تم حذف البلف بنجاح.')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'حدث خطأ أثناء حذف البلف: {e}')
        
    return redirect('valve-list-frontend')