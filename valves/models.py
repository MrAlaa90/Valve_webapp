import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def get_valve_image_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/valves/<tag_number>/<category>/<filename>
    return os.path.join('valves', instance.valve.tag_number, instance.category, filename)

def get_maintenance_image_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/maintenance/<valve_tag_number>/<maintenance_id>/<filename>
    return os.path.join('maintenance', instance.valve.tag_number, str(instance.maintenance_id), filename)

class ValveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class ValveStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

    def get_status_color(self):
        """Returns a Bootstrap color class based on the status name."""
        name_lower = self.name.lower()
        if 'operational' in name_lower or 'good' in name_lower:
            return 'success'
        elif 'needs maintenance' in name_lower or 'fair' in name_lower:
            return 'warning'
        elif 'critical' in name_lower or 'out of service' in name_lower:
            return 'danger'
        return 'secondary' # Default color

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Technician(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Factory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_color(self):
        """Returns a Bootstrap color class based on the factory name."""
        if self.name == 'AFC I':
            return 'danger'
        elif self.name == 'AFC II':
            return 'success'
        elif self.name == 'AFC III':
            return 'primary'
        # Default for ZLD or any other factory
        return 'info'

class Valve(models.Model):
    valve_id = models.AutoField(primary_key=True)
    tag_number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    valve_type = models.ForeignKey(ValveType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(ValveStatus, on_delete=models.SET_NULL, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True)
    factory = models.ForeignKey(Factory, on_delete=models.SET_NULL, null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    drawing_link = models.URLField(max_length=500, null=True, blank=True)
    model_number = models.CharField(max_length=255, null=True, blank=True)
    shut_off_pressure = models.CharField(max_length=255, null=True, blank=True)
    power_failure_pos = models.CharField(max_length=255, null=True, blank=True)
    body_style = models.CharField(max_length=255, null=True, blank=True)
    required_travel_angle = models.CharField(max_length=255, null=True, blank=True)
    bench_range = models.CharField(max_length=255, null=True, blank=True)
    plug_stem_mat = models.CharField(max_length=255, null=True, blank=True)
    butterfly_shaft_mat = models.CharField(max_length=255, null=True, blank=True)
    seat_guide_mat = models.CharField(max_length=255, null=True, blank=True)
    seat_diameter = models.CharField(max_length=255, null=True, blank=True)
    trim_coating = models.CharField(max_length=255, null=True, blank=True)
    leakage_class = models.CharField(max_length=255, null=True, blank=True)
    packing_mat = models.CharField(max_length=255, null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.tag_number

class Shutdown(models.Model):
    name = models.CharField(max_length=255)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    valves = models.ManyToManyField(Valve)
    def __str__(self):
        return self.name



class SparePart(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True, unique=True)
    part_name = models.CharField(max_length=255)

    def __str__(self):
        return self.part_name

class PartCode(models.Model):
    part_code_id = models.AutoField(primary_key=True)
    sap_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    oracle_code = models.CharField(max_length=100, null=True, blank=True)
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    unit_price = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    associated_valves = models.ManyToManyField(Valve, blank=True, related_name='part_codes')
    condition = models.CharField(max_length=255, null=True, blank=True)
    part_number = models.CharField(max_length=100, null=True, blank=True)
    manufacturer_co = models.CharField(max_length=255, null=True, blank=True)
    unit_of_measure = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.sap_code or self.oracle_code or self.part_number

class MaintenanceHistory(models.Model):
    maintenance_id = models.AutoField(primary_key=True)
    valve = models.ForeignKey(Valve, on_delete=models.CASCADE, related_name='maintenance_records')
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True)
    maintenance_date = models.DateField()
    oracle_code = models.CharField(max_length=255, null=True, blank=True)
    maintenance_activities = models.CharField(max_length=500, blank=True, null=True)
    maintenance_notes = models.TextField(null=True, blank=True)
    pressure_test = models.CharField(max_length=255, null=True, blank=True)
    testing_pressure = models.FloatField(null=True, blank=True)
    is_shutdown = models.BooleanField(default=False, verbose_name="Shutdown")
    is_active = models.BooleanField(default=True)
    before_image = models.ImageField(upload_to=get_maintenance_image_upload_path, verbose_name="Before Image", null=True, blank=True)
    after_image = models.ImageField(upload_to=get_maintenance_image_upload_path, verbose_name="After Image", null=True, blank=True)

    def __str__(self):
        return f"Maintenance for {self.valve.tag_number} on {self.maintenance_date}"

class MaintenancePart(models.Model):
    maintenance_part_id = models.AutoField(primary_key=True)
    maintenance_event = models.ForeignKey(MaintenanceHistory, on_delete=models.CASCADE)
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE, null=True, blank=True)
    code = models.ForeignKey(PartCode, on_delete=models.CASCADE, null=True, blank=True)
    quantity_used = models.FloatField(default=1.0)
    associated_activity = models.CharField(max_length=255, null=True, blank=True)
    entered_code = models.CharField(max_length=255, null=True, blank=True)

class ValveImage(models.Model):
    IMAGE_CATEGORIES = [
        ('Valves_Specs', 'Valve Specs'),
        ('P&ID', 'P&ID'),
        ('Maintenance_Reports', 'Maintenance Reports'),
    ]
    valve = models.ForeignKey(Valve, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_valve_image_upload_path, verbose_name="Image")
    category = models.CharField(max_length=100, choices=IMAGE_CATEGORIES, default='Valves_Specs', verbose_name="Image Category")
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.valve.tag_number} - {self.get_category_display()}"


class UserProfile(models.Model):
    """
    ملف تعريف المستخدم وصلاحياته وتكليفاته داخل منظومة الورشة.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin - مدير النظام (صلاحيات كاملة)'),
        ('supervisor', 'Supervisor - مهندس / مشرف صيانة'),
        ('technician', 'Technician - فني صيانة ميداني'),
        ('viewer', 'Viewer - مشاهد فقط (للاطلاع والقراءة)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='technician', verbose_name="الدور والصلاحية")
    factory = models.ForeignKey(Factory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المصنع المسؤول عنه")
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="فني الصيانة المرتبط")
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الهاتف")
    can_export = models.BooleanField(default=True, verbose_name="صلاحية تصدير البيانات (Excel/CSV)")
    can_import = models.BooleanField(default=False, verbose_name="صلاحية استيراد البيانات (Excel/CSV)")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات وتكليفات")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def role_badge_color(self):
        colors = {
            'admin': 'danger',
            'supervisor': 'warning text-dark',
            'technician': 'primary',
            'viewer': 'secondary',
        }
        return colors.get(self.role, 'info')

    def has_export_perm(self):
        """التحقق من صلاحية تصدير البيانات"""
        if self.user.is_superuser or self.role == 'admin':
            return True
        return self.can_export

    def has_import_perm(self):
        """التحقق من صلاحية استيراد البيانات"""
        if self.user.is_superuser or self.role == 'admin':
            return True
        return self.can_import

    @property
    def permissions_summary(self):
        """قائمة الصلاحيات الفعلية الممنوحة للمستخدم داخل المنظومة"""
        if self.role == 'admin' or self.user.is_superuser:
            return [
                "إدارة المستخدمين والصلاحيات (إضافة / تعديل / حذف)",
                "إدارة وتعديل الصمامات والمواصفات الهندسية",
                "تسجيل وتعديل سجلات الصيانة وقراءات الاختبار",
                "إدارة قطع الغيار وأكواد SAP/Oracle والمخزون",
                "توليد وطباعة تقارير العمرة والشداون",
                "إنشاء واستعادة النسخ الاحتياطية وتصديرها لـ USB",
                "تصدير واستيراد بيانات كافة الجداول (Excel / CSV)",
                "تحميل قوالب الجداول المعتمدة للاستيراد والتصدير",
                "الوصول للوحة تحكم إدارة دجانغو (Admin Panel)",
            ]
        elif self.role == 'supervisor':
            perms = [
                "إدارة وتعديل الصمامات والمواصفات الفنية",
                "تسجيل وتعديل سجلات الصيانة وقراءات الاختبار",
                "إدارة قطع الغيار وأكواد SAP/Oracle والمخزون",
                "توليد وطباعة تقارير العمرة والشداون",
                "إنشاء نسخ احتياطية يدوية للنظام",
            ]
            if self.has_export_perm():
                perms.append("تصدير بيانات الجداول (Excel / CSV)")
            if self.has_import_perm():
                perms.append("استيراد بيانات الجداول (Excel / CSV)")
            return perms
        elif self.role == 'technician':
            perms = [
                "تسجيل عمليات الصيانة الميدانية وربط قطع الغيار المستخدمة",
                "رفع صور الصيانة (قبل وبعد الإصلاح)",
                "البحث واستعراض الصمامات وقطع الغيار",
                "الاطلاع على مستندات ومخططات P&ID",
            ]
            if self.has_export_perm():
                perms.append("تصدير سجلات الصيانة والجداول (Excel / CSV)")
            if self.has_import_perm():
                perms.append("استيراد بيانات الجداول (Excel / CSV)")
            return perms
        else:  # viewer
            perms = [
                "استعراض الصمامات والبحث في المواصفات الهندسية",
                "استعراض سجلات الصيانة السابقة للمصانع",
                "الاطلاع على التقارير والمستندات (للقراءة فقط)",
            ]
            if self.has_export_perm():
                perms.append("تصدير بيانات الجداول (Excel / CSV)")
            return perms


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else ('supervisor' if instance.is_staff else 'technician')
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})

