from valves import models

def run_data_cleanup():
    """
    يقوم بحذف جميع بيانات PartCode و SparePart من قاعدة البيانات
    لأغراض الاختبار وإعادة التحميل.
    """
    print("--- بدء عملية تنظيف بيانات قطع الغيار ---")
    
    # حذف جميع PartCode أولاً لأنها تعتمد على SparePart (Foreign Key)
    part_code_count = models.PartCode.objects.all().count()
    if part_code_count > 0:
        print(f"جاري حذف {part_code_count} سجل PartCode...")
        models.PartCode.objects.all().delete()
        print("✅ تم حذف PartCode بنجاح.")
    else:
        print("ℹ️ لا يوجد سجلات PartCode لحذفها.")

    # حذف جميع SparePart ثانياً
    spare_part_count = models.SparePart.objects.all().count()
    if spare_part_count > 0:
        print(f"جاري حذف {spare_part_count} سجل SparePart...")
        models.SparePart.objects.all().delete()
        print("✅ تم حذف SparePart بنجاح.")
    else:
        print("ℹ️ لا يوجد سجلات SparePart لحذفها.")

    print("--- اكتملت عملية التنظيف ---")
