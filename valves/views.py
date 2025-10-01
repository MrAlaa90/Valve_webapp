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




def home(request):
    """
    View for the home page, including statistics about the valves.
    """
    try:
        total_valves = Valve.objects.count()
        # نفترض أن لديك حالات مثل 'Needs Maintenance' و 'Operational' في نموذج Valve
        # قم بتعديل هذه القيم لتطابق القيم الفعلية في حقل 'status' لديك
        needs_maintenance_valves = Valve.objects.filter(status='Needs Maintenance').count()
        operational_valves = Valve.objects.filter(status='Operational').count()
    except Exception:
        # في حالة حدوث أي خطأ، نعرض أصفارًا كقيم افتراضية
        total_valves = needs_maintenance_valves = operational_valves = 0
        messages.warning(request, "لم يتم تحميل الإحصائيات بشكل صحيح.")
    context = {
        'total_valves': total_valves,
        'needs_maintenance_valves': needs_maintenance_valves,
        'operational_valves': operational_valves,
    }
    return render(request, 'valves/home.html', context)
@login_required
def valve_list_frontend(request):
      # هنا هنجلب البيانات من الـ API الخاص بينا
    api_url = request.build_absolute_uri('/valves/api/valves/') # بناء رابط الـ API بشكل صحيح
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
    # api_url = f"http://127.0.0.1:8000/api/valves/{pk}/"
    api_url = request.build_absolute_uri(f'/valves/api/valves/{pk}/')
    valve_data = None
    maintenance_records = []
    spare_parts = []
    error_message = None
    try:
        response = requests.get(api_url)
        response.raise_for_status() # هيرفع HTTPError لو الـ request فشلت
        valve_data = response.json()

        # بعد جلب بيانات البلف بنجاح، نجلب البيانات المرتبطة به
        if valve_data:
            # جلب سجلات الصيانة المرتبطة بالبلف
            maintenance_api_url = request.build_absolute_uri(f'/valves/api/maintenance-history/?valve={pk}')
            maintenance_response = requests.get(maintenance_api_url)
            if maintenance_response.status_code == 200:
                maintenance_records = maintenance_response.json()

            # يمكنك إضافة منطق مشابه لجلب قطع الغيار المرتبطة هنا إذا كان الـ API يدعم ذلك
            # spare_parts_api_url = request.build_absolute_uri(f'/api/spare-parts/?valve={pk}')
            # ...

    except requests.exceptions.HTTPError as err:
        # التعامل مع خطأ 404 لو البلف مش موجود
        if response.status_code == 404:
            error_message = f"البلف برقم {pk} غير موجود."
        else:
            error_message = f"خطأ في HTTP أثناء جلب البيانات: {err}"      
    except requests.exceptions.RequestException as e:
        error_message = f"خطأ في الاتصال بالـ API: {e}"
    
    context = {
        'valve': valve_data,
        'maintenance_records': maintenance_records,
        'spare_parts': spare_parts, # حتى لو كانت فارغة حالياً، نمررها للقالب
        'pk': pk,
        'error': error_message
    }    
    return render(request, 'valves/valve_detail.html', context)

@login_required
def valve_create_frontend(request):
    """
    عرض نموذج إنشاء بلف جديد.
    (تم تبسيط هذه الدالة لتعتمد على JavaScript في القالب لإرسال البيانات عبر API POST).
    """
    context = {
        'title': 'إضافة بلف جديد',
        'is_edit': False,
        'pk': None 
    }
    # هنا يتم عرض القالب الذي يحتوي على منطق الـ API في JavaScript
    return render(request, 'valves/valve_form.html', context)


@login_required
def valve_update_frontend(request, pk):
    """
    عرض نموذج تعديل بلف موجود.
    (تم تبسيط هذه الدالة لتعتمد على JavaScript في القالب لجلب البيانات وإرسال التعديلات عبر API PUT).
    """
    context = {
        'title': f'تعديل البلف رقم {pk}',
        'is_edit': True,
        'pk': pk # تمرير المفتاح الرئيسي لتشغيل منطق الجلب والتعديل في JavaScript
    }
    # هنا يتم عرض القالب الذي يحتوي على منطق الـ API في JavaScript
    return render(request, 'valves/valve_form.html', context)

@login_required
def spare_part_form_frontend(request, pk=None):
    """
    Handles the frontend form for creating or updating a Spare Part.
    It fetches or sends data to the internal API endpoints.
    """
    api_base_url = request.build_absolute_uri('/valves/api/spare-parts/')
    is_update = pk is not None
    part_data = None
    error_message = None

    # 1. GET request: Fetch existing data for update
    if is_update:
        api_detail_url = f'{api_base_url}{pk}/'
        try:
            response = requests.get(api_detail_url)
            response.raise_for_status()
            part_data = response.json()
        except requests.exceptions.RequestException as err:
            error_message = f"فشل في جلب بيانات قطعة الغيار: {err}"
            messages.error(request, error_message)

    # 2. POST request: Handle form submission (Create or Update)
    if request.method == 'POST':
        form_data = {
            'part_number': request.POST.get('part_number'),
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'quantity_in_stock': request.POST.get('quantity_in_stock'),
            'min_stock_level': request.POST.get('min_stock_level'),
            'unit_of_measure': request.POST.get('unit_of_measure'),
        }

        try:
            if is_update:
                # PUT for update
                response = requests.put(api_detail_url, json=form_data)
                action_text = "تعديل"
            else:
                # POST for create
                response = requests.post(api_base_url, json=form_data)
                action_text = "إضافة"

            response.raise_for_status()

            # في حالة النجاح
            messages.success(request, f"تم {action_text} قطعة الغيار بنجاح!")
            if not is_update:
                # بعد الإضافة، إعادة توجيه إلى صفحة القائمة
                return redirect('valves:spare-part-list-frontend')
            else:
                # في حالة التعديل، قم بتحديث البيانات المعروضة
                part_data = response.json()

        except requests.exceptions.HTTPError as err:
            # معالجة أخطاء الـ API (مثل 400 Bad Request)
            error_details = response.json() if response.status_code == 400 else str(err)
            error_message = f"فشل في {action_text} قطعة الغيار: {error_details}"
            messages.error(request, error_message)
        except requests.exceptions.RequestException as err:
            error_message = f"خطأ في الاتصال بالـ API: {err}"
            messages.error(request, error_message)

    context = {
        'part': part_data,
        'pk': pk,
        'is_update': is_update,
        'error': error_message
    }
    return render(request, 'valves/spare_part_form.html', context)



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
    """
    التعامل مع طلب حذف بلف معين عبر الـ API (DELETE).
    الصفحة دي تعرض نموذج تأكيد الحذف.
    """
    api_detail_url = request.build_absolute_uri(f'/valves/api/valves/{pk}/')
    
    # 1. في حالة طلب GET: بنعرض صفحة تأكيد الحذف
    if request.method == 'GET':
        valve_data = {}
        try:
            # بنجيب البيانات بس عشان نعرض اسم البلف في رسالة التأكيد
            response = requests.get(api_detail_url)
            response.raise_for_status() 
            valve_data = response.json()
        except requests.exceptions.RequestException as e:
            messages.error(request, f"خطأ: فشل جلب بيانات البلف رقم {pk}. {e}")
            return redirect('valves:valve-list-frontend')
            
        context = {
            'valve': valve_data,
            'pk': pk
        }
        return render(request, 'valves/valve_confirm_delete.html', context)

    # 2. في حالة طلب POST: بننفذ عملية الحذف
    elif request.method == 'POST':
        try:
            response = requests.delete(api_detail_url)
            # 204 No Content هو الرد الطبيعي للحذف الناجح
            if response.status_code == 204:
                messages.success(request, f"تم حذف البلف رقم {pk} بنجاح.")
            else:
                response.raise_for_status() # لو فيه أي خطأ تاني (4xx, 5xx)
            
            # التوجيه لقائمة البلوف بعد الحذف
            return redirect('valves:valve-list-frontend')
            
        except requests.exceptions.HTTPError as err:
            messages.error(request, f"خطأ في الحذف: البلف رقم {pk} لم يتم حذفه. {err}")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"خطأ في الاتصال بالشبكة أثناء محاولة الحذف: {e}")
            
        # لو فشل الحذف، نرجع لصفحة القائمة
        return redirect('valves:valve-list-frontend')


@login_required
def part_code_form_frontend(request, pk=None):
    """
    Handles the frontend form for creating or updating a Part Code.
    It fetches or sends data to the internal API endpoints.
    """
    api_base_url = request.build_absolute_uri('/valves/api/part-codes/')
    is_update = pk is not None
    code_data = None
    error_message = None

    if is_update:
        api_detail_url = f'{api_base_url}{pk}/'
        # 1. GET request for existing data
        try:
            response = requests.get(api_detail_url)
            response.raise_for_status()
            code_data = response.json()
        except requests.exceptions.HTTPError as err:
            error_message = f"فشل في جلب بيانات كود القطعة: {err}"
            messages.error(request, error_message)
        except requests.exceptions.RequestException as err:
            error_message = f"خطأ في الاتصال بالـ API: {err}"
            messages.error(request, error_message)

    if request.method == 'POST':
        # 2. POST/PUT request for form submission
        form_data = {
            'code_number': request.POST.get('code_number'),
            'description': request.POST.get('description'),
            'standard_unit': request.POST.get('standard_unit'),
            'associated_valve': request.POST.get('associated_valve'), # يجب التأكد أن هذا يمرر ID
        }

        try:
            if is_update:
                # PUT for update
                response = requests.put(api_detail_url, json=form_data)
                action_text = "تعديل"
            else:
                # POST for create
                response = requests.post(api_base_url, json=form_data)
                action_text = "إضافة"
            
            response.raise_for_status()
            
            # في حالة النجاح
            messages.success(request, f"تم {action_text} كود القطعة بنجاح!")
            if not is_update:
                 # بعد الإضافة، إعادة توجيه إلى صفحة القائمة أو التفاصيل
                return redirect('valves:part-code-list-frontend')
            else:
                # في حالة التعديل، قم بتحديث البيانات المعروضة
                code_data = response.json()


        except requests.exceptions.HTTPError as err:
            # معالجة أخطاء الـ API (مثل 400 Bad Request)
            error_message = f"فشل في {action_text} كود القطعة: {response.text}"
            messages.error(request, error_message)
        except requests.exceptions.RequestException as err:
            error_message = f"خطأ في الاتصال بالـ API: {err}"
            messages.error(request, error_message)
    UNIT_CHOICES = ['Piece', 'Meter', 'KG', 'Liter']
    context = {
        'code': code_data,
        'pk': pk,
        'is_update': is_update,
        'unit_choices': UNIT_CHOICES,
        # 'valve_choices': [قائمة بالبلوف للمساعدة في تحديد البلف المرتبط]
    }
    return render(request, 'valves/part_code_form.html', context)

@login_required
def maintenance_form_frontend(request, pk=None):
    """
    عرض نموذج إنشاء أو تعديل سجل صيانة (Maintenance Record Form).
    
    الهدف: عرض النموذج وتجهيز البيانات الأولية للبلف إذا كان وضع إنشاء جديد.
    """
    context = {
        'pk': pk,
        'title': 'إضافة سجل صيانة جديد' if pk is None else 'تعديل سجل صيانة',
        'is_edit': pk is not None
    }

    # إذا كان المستخدم قادماً من صفحة تفاصيل البلف (للإنشاء)
    if 'valve_id' in request.GET and pk is None:
         # هنا يجب أن نستخدم valve_id لطلب بيانات البلف من الـ API 
         # وتمريرها للقالب كبيانات أولية (سنقوم بتنفيذ هذا لاحقاً).
         context['initial_valve_id'] = request.GET.get('valve_id')

    # حالياً، نعرض القالب فقط لحل مشكلة ImportError
    return render(request, 'valves/maintenance_form.html', context)