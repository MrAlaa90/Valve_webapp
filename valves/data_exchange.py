"""
Universal Data Exchange Engine for Valve Workshop Management System.

Provides:
- Bidirectional Excel (.xlsx) and CSV export/import for all system tables.
- Official Data Dictionary & Multi-Sheet Excel Template Generator.
- Robust transaction-safe upsert mechanisms with foreign-key auto-resolution.
- Comprehensive import validation with detailed error tracking.
"""

import io
import csv
from datetime import datetime, date
from django.db import transaction
from django.http import HttpResponse
from django.utils.text import slugify

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .models import (
    Valve, ValveType, ValveStatus, Manufacturer, Factory, Technician,
    Shutdown, SparePart, PartCode, MaintenanceHistory
)

# Supported Tables Definition
SUPPORTED_TABLES = {
    'valves': {
        'name_ar': 'الصمامات والمواصفات الهندسية',
        'name_en': 'Valves & Specifications',
        'model': Valve,
        'unique_field': 'tag_number',
        'columns': [
            {'key': 'tag_number', 'label_ar': 'رقم كود الصمام (Tag Number)', 'required': True, 'sample': '10-FV-001'},
            {'key': 'name', 'label_ar': 'اسم / وصف الصمام', 'required': True, 'sample': 'Feed Gas Flow Control Valve'},
            {'key': 'location', 'label_ar': 'الموقع / الوحدة', 'required': False, 'sample': 'Primary Reformer Area'},
            {'key': 'factory', 'label_ar': 'المصنع التابع له', 'required': False, 'sample': 'AFC I'},
            {'key': 'valve_type', 'label_ar': 'نوع الصمام', 'required': False, 'sample': 'Globe Valve'},
            {'key': 'status', 'label_ar': 'حالة الصمام التشغيلية', 'required': False, 'sample': 'Operational'},
            {'key': 'manufacturer', 'label_ar': 'الشركة المصنعة', 'required': False, 'sample': 'Fisher'},
            {'key': 'model_number', 'label_ar': 'رقم الموديل', 'required': False, 'sample': 'ED-100'},
            {'key': 'shut_off_pressure', 'label_ar': 'ضغط الغلق (Shut Off)', 'required': False, 'sample': '25 bar'},
            {'key': 'power_failure_pos', 'label_ar': 'حالة انقطاع الهواء (Fail Pos)', 'required': False, 'sample': 'Fail Closed'},
            {'key': 'body_style', 'label_ar': 'نوع جسم الصمام', 'required': False, 'sample': 'Cast Steel'},
            {'key': 'required_travel_angle', 'label_ar': 'مشوار الحركة / الزاوية', 'required': False, 'sample': '2 inch'},
            {'key': 'bench_range', 'label_ar': 'نطاق التشغيل (Bench Range)', 'required': False, 'sample': '3-15 psi'},
            {'key': 'seat_diameter', 'label_ar': 'قطر المقعد (Seat Diameter)', 'required': False, 'sample': '4 inch'},
            {'key': 'leakage_class', 'label_ar': 'فئة التسريب (Leakage Class)', 'required': False, 'sample': 'Class IV'},
            {'key': 'installation_date', 'label_ar': 'تاريخ التركيب (YYYY-MM-DD)', 'required': False, 'sample': '2020-01-15'},
            {'key': 'last_maintenance_date', 'label_ar': 'تاريخ آخر صيانة (YYYY-MM-DD)', 'required': False, 'sample': '2025-06-10'},
            {'key': 'notes', 'label_ar': 'ملاحظات وتفاصيل فنية', 'required': False, 'sample': 'Calibrated during turnaround'},
        ]
    },
    'maintenance': {
        'name_ar': 'سجلات وتقارير الصيانة والفحص',
        'name_en': 'Maintenance & Testing Records',
        'model': MaintenanceHistory,
        'unique_field': None,  # Inserts new records or matches on (valve, maintenance_date)
        'columns': [
            {'key': 'valve_tag', 'label_ar': 'رقم كود الصمام (Tag Number)', 'required': True, 'sample': '10-FV-001'},
            {'key': 'maintenance_date', 'label_ar': 'تاريخ تنفيذ الصيانة (YYYY-MM-DD)', 'required': True, 'sample': '2025-08-20'},
            {'key': 'technician_name', 'label_ar': 'اسم الفني أو المشرف', 'required': False, 'sample': 'أحمد إبراهيم'},
            {'key': 'oracle_code', 'label_ar': 'رقم أمر الشغل / Oracle Code', 'required': False, 'sample': 'WO-98421'},
            {'key': 'maintenance_activities', 'label_ar': 'الأنشطة المنفذة', 'required': False, 'sample': 'Lapping, Gasket replacement'},
            {'key': 'maintenance_notes', 'label_ar': 'ملاحظات الصيانة وتقرير الفحص', 'required': False, 'sample': 'Replaced packing, passed hydrostatic test'},
            {'key': 'pressure_test', 'label_ar': 'نتيجة اختبار الضغط', 'required': False, 'sample': 'Passed'},
            {'key': 'testing_pressure', 'label_ar': 'ضغط الاختبار المقاس (bar)', 'required': False, 'sample': '35.0'},
            {'key': 'is_shutdown', 'label_ar': 'عمرة / شداون؟ (نعم/لا)', 'required': False, 'sample': 'نعم'},
        ]
    },
    'part_codes': {
        'name_ar': 'أكواد ومخزون قطع الغيار',
        'name_en': 'Part Codes & Warehouse Stock',
        'model': PartCode,
        'unique_field': 'sap_code',
        'columns': [
            {'key': 'sap_code', 'label_ar': 'كود ساب (SAP Code)', 'required': True, 'sample': '10045231'},
            {'key': 'oracle_code', 'label_ar': 'كود أوراكل (Oracle Code)', 'required': False, 'sample': 'OR-55412'},
            {'key': 'part_name', 'label_ar': 'اسم قطعة الغيار الأساسية', 'required': True, 'sample': 'Gland Packing Set'},
            {'key': 'part_number', 'label_ar': 'رقم القطعة (Part Number)', 'required': False, 'sample': 'FSH-4421-A'},
            {'key': 'manufacturer_co', 'label_ar': 'الشركة المصنعة للقطعة', 'required': False, 'sample': 'Fisher Controls'},
            {'key': 'description', 'label_ar': 'الوصف الفني التفصيلي', 'required': False, 'sample': 'PTFE V-Ring Packing 2 inch'},
            {'key': 'quantity', 'label_ar': 'الكمية المتوفرة بالمخزن', 'required': False, 'sample': '15'},
            {'key': 'unit_price', 'label_ar': 'سعر الوحدة', 'required': False, 'sample': '250.0'},
            {'key': 'location', 'label_ar': 'مكان التخزين / الرف (Bin)', 'required': False, 'sample': 'Warehouse B - Shelf 04'},
            {'key': 'category', 'label_ar': 'تصنيف القطعة', 'required': False, 'sample': 'Packings & Seals'},
            {'key': 'unit_of_measure', 'label_ar': 'وحدة القياس', 'required': False, 'sample': 'Set'},
        ]
    },
    'factories': {
        'name_ar': 'المصانع والقطاعات الإنتاجية',
        'name_en': 'Factories & Plants',
        'model': Factory,
        'unique_field': 'name',
        'columns': [
            {'key': 'name', 'label_ar': 'اسم المصنع أو الوحدة الإنتاجية', 'required': True, 'sample': 'AFC I'},
        ]
    },
    'technicians': {
        'name_ar': 'فنيي ومهندسي الصيانة',
        'name_en': 'Maintenance Technicians',
        'model': Technician,
        'unique_field': 'name',
        'columns': [
            {'key': 'name', 'label_ar': 'اسم الفني بالكامل', 'required': True, 'sample': 'محمد علي'},
        ]
    },
    'valve_types': {
        'name_ar': 'أنواع وتصنيفات الصمامات',
        'name_en': 'Valve Types',
        'model': ValveType,
        'unique_field': 'name',
        'columns': [
            {'key': 'name', 'label_ar': 'نوع الصمام (Control, Ball, Gate, ...)', 'required': True, 'sample': 'Control Valve'},
        ]
    },
    'valve_statuses': {
        'name_ar': 'حالات الصمامات التشغيلية',
        'name_en': 'Valve Statuses',
        'model': ValveStatus,
        'unique_field': 'name',
        'columns': [
            {'key': 'name', 'label_ar': 'اسم الحالة التشغيلية', 'required': True, 'sample': 'Operational'},
        ]
    },
    'manufacturers': {
        'name_ar': 'الشركات المصنعة',
        'name_en': 'Manufacturers',
        'model': Manufacturer,
        'unique_field': 'name',
        'columns': [
            {'key': 'name', 'label_ar': 'اسم الشركة المصنعة', 'required': True, 'sample': 'Emerson / Fisher'},
        ]
    },
    'shutdowns': {
        'name_ar': 'فترات التوقف والعمرات (Shutdowns)',
        'name_en': 'Shutdown Turnarounds',
        'model': Shutdown,
        'unique_field': 'name',
        'columns': [
            {'key': 'name', 'label_ar': 'اسم العمرة / الشداون', 'required': True, 'sample': 'Turnaround 2025 Q3'},
            {'key': 'factory', 'label_ar': 'المصنع التابع له', 'required': False, 'sample': 'AFC II'},
            {'key': 'start_date', 'label_ar': 'تاريخ البداية (YYYY-MM-DD)', 'required': True, 'sample': '2025-09-01'},
            {'key': 'end_date', 'label_ar': 'تاريخ النهاية (YYYY-MM-DD)', 'required': True, 'sample': '2025-09-21'},
        ]
    }
}


def get_supported_tables_metadata():
    """Returns friendly metadata summary for all supported tables."""
    meta = []
    for key, spec in SUPPORTED_TABLES.items():
        count = spec['model'].objects.count()
        meta.append({
            'key': key,
            'name_ar': spec['name_ar'],
            'name_en': spec['name_en'],
            'count': count,
            'unique_field': spec['unique_field'] or 'Auto',
            'columns_count': len(spec['columns'])
        })
    return meta


# ==============================================================================
# 1. EXCEL TEMPLATES WORKBOOK GENERATOR
# ==============================================================================

def generate_excel_templates_workbook() -> bytes:
    """
    Generates a professionally styled multi-sheet Excel workbook containing:
    1. Table of Contents & Instructions Sheet (فهرس الجداول المعتمدة).
    2. Ready-to-use template sheets with pre-filled sample rows for each table.
    """
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styling definitions (Abu Qir Fertilizers corporate colors)
    brand_blue = "004A99"
    brand_header_fill = PatternFill(start_color=brand_blue, end_color=brand_blue, fill_type="solid")
    brand_header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

    catalog_header_fill = PatternFill(start_color="198754", end_color="198754", fill_type="solid")
    catalog_header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

    sub_header_fill = PatternFill(start_color="E9ECEF", end_color="E9ECEF", fill_type="solid")
    sub_header_font = Font(name="Arial", size=10, bold=True, color="212529")

    sample_row_fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
    regular_font = Font(name="Arial", size=10, color="212529")
    bold_font = Font(name="Arial", size=10, bold=True, color="212529")

    thin_border = Border(
        left=Side(style='thin', color='DEE2E6'),
        right=Side(style='thin', color='DEE2E6'),
        top=Side(style='thin', color='DEE2E6'),
        bottom=Side(style='thin', color='DEE2E6')
    )

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    right_align = Alignment(horizontal="right", vertical="center", wrap_text=True)

    # -------------------------------------------------------------------------
    # Sheet 1: Catalog & Data Dictionary
    # -------------------------------------------------------------------------
    ws_cat = wb.create_sheet(title="فهرس_الجداول_المعتمدة")
    ws_cat.views.sheetView[0].rightToLeft = True

    # Title Banner
    ws_cat.merge_cells("A1:E1")
    title_cell = ws_cat["A1"]
    title_cell.value = "دليل وفهرس جداول الاستيراد والتصدير - منظومة ورشة الصمامات (Valve Workshop)"
    title_cell.font = Font(name="Arial", size=14, bold=True, color="004A99")
    title_cell.alignment = center_align
    ws_cat.row_dimensions[1].height = 35

    # Instructions
    ws_cat.merge_cells("A2:E2")
    ws_cat["A2"].value = "ملاحظات هامة: التواريخ بصيغة YYYY-MM-DD. في حال وجود سجل سابق بنفس الكود يتم تحديثه تلقائياً بدون تكرار."
    ws_cat["A2"].font = Font(name="Arial", size=10, italic=True, color="6C757D")
    ws_cat["A2"].alignment = center_align
    ws_cat.row_dimensions[2].height = 25

    # Table Header
    headers = ["رمز الجدول البرمجي", "اسم الشاشة / الجدول بالعربية", "الاسم بالإنجليزية", "مفتاح الربط الفريد", "عدد الحقول"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws_cat.cell(row=4, column=col_idx, value=h)
        cell.fill = catalog_header_fill
        cell.font = catalog_header_font
        cell.alignment = center_align
        cell.border = thin_border
    ws_cat.row_dimensions[4].height = 28

    current_row = 5
    for key, spec in SUPPORTED_TABLES.items():
        row_vals = [
            key,
            spec['name_ar'],
            spec['name_en'],
            spec['unique_field'] or 'تلقائي (إضافة جديدة)',
            len(spec['columns'])
        ]
        for col_idx, val in enumerate(row_vals, 1):
            cell = ws_cat.cell(row=current_row, column=col_idx, value=val)
            cell.font = bold_font if col_idx <= 2 else regular_font
            cell.alignment = center_align if col_idx in [1, 4, 5] else right_align
            cell.border = thin_border
            if current_row % 2 == 0:
                cell.fill = sample_row_fill
        ws_cat.row_dimensions[current_row].height = 22
        current_row += 1

    # Auto-fit columns
    for col in ws_cat.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_cat.column_dimensions[col_letter].width = max(max_len + 4, 15)

    # -------------------------------------------------------------------------
    # Sheets 2..N: Table Templates
    # -------------------------------------------------------------------------
    for key, spec in SUPPORTED_TABLES.items():
        sheet_title = f"{key[:15]}"
        ws = wb.create_sheet(title=sheet_title)
        ws.views.sheetView[0].rightToLeft = True

        # Header Row 1: Keys (used by import parser)
        # Header Row 2: Friendly Arabic Labels
        cols = spec['columns']

        for col_idx, col_spec in enumerate(cols, 1):
            # Row 1: English Key (Exact)
            c1 = ws.cell(row=1, column=col_idx, value=col_spec['key'])
            c1.fill = brand_header_fill
            c1.font = brand_header_font
            c1.alignment = center_align
            c1.border = thin_border

            # Row 2: Arabic Description
            req_mark = " (مطلوب)" if col_spec.get('required') else ""
            c2 = ws.cell(row=2, column=col_idx, value=col_spec['label_ar'] + req_mark)
            c2.fill = sub_header_fill
            c2.font = sub_header_font
            c2.alignment = center_align
            c2.border = thin_border

            # Row 3: Sample value
            c3 = ws.cell(row=3, column=col_idx, value=col_spec.get('sample', ''))
            c3.fill = sample_row_fill
            c3.font = regular_font
            c3.alignment = center_align
            c3.border = thin_border

        ws.row_dimensions[1].height = 24
        ws.row_dimensions[2].height = 24
        ws.row_dimensions[3].height = 22

        # Auto-fit columns
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 5, 18)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ==============================================================================
# 2. UNIVERSAL EXPORT ENGINE
# ==============================================================================

def export_table_to_response(table_key: str, file_format: str = 'xlsx') -> HttpResponse:
    """
    Exports all records of the given table as a downloadable Excel (.xlsx) or CSV file.
    """
    if table_key not in SUPPORTED_TABLES:
        raise ValueError(f"Table '{table_key}' is not supported for export.")

    spec = SUPPORTED_TABLES[table_key]
    model = spec['model']
    cols = spec['columns']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"ValveWorkshop_{table_key}_{timestamp}"

    # Extract rows based on table specifications
    rows = []
    qs = model.objects.all()

    # Optimized queryset fetches
    if table_key == 'valves':
        qs = qs.select_related('valve_type', 'status', 'manufacturer', 'factory')
        for v in qs:
            rows.append({
                'tag_number': v.tag_number,
                'name': v.name,
                'location': v.location,
                'factory': v.factory.name if v.factory else '',
                'valve_type': v.valve_type.name if v.valve_type else '',
                'status': v.status.name if v.status else '',
                'manufacturer': v.manufacturer.name if v.manufacturer else '',
                'model_number': v.model_number or '',
                'shut_off_pressure': v.shut_off_pressure or '',
                'power_failure_pos': v.power_failure_pos or '',
                'body_style': v.body_style or '',
                'required_travel_angle': v.required_travel_angle or '',
                'bench_range': v.bench_range or '',
                'seat_diameter': v.seat_diameter or '',
                'leakage_class': v.leakage_class or '',
                'installation_date': v.installation_date.isoformat() if v.installation_date else '',
                'last_maintenance_date': v.last_maintenance_date.isoformat() if v.last_maintenance_date else '',
                'notes': v.notes or '',
            })
    elif table_key == 'maintenance':
        qs = qs.select_related('valve', 'technician').order_by('-maintenance_date')
        for m in qs:
            rows.append({
                'valve_tag': m.valve.tag_number if m.valve else '',
                'maintenance_date': m.maintenance_date.isoformat() if m.maintenance_date else '',
                'technician_name': m.technician.name if m.technician else '',
                'oracle_code': m.oracle_code or '',
                'maintenance_activities': m.maintenance_activities or '',
                'maintenance_notes': m.maintenance_notes or '',
                'pressure_test': m.pressure_test or '',
                'testing_pressure': str(m.testing_pressure or ''),
                'is_shutdown': 'نعم' if m.is_shutdown else 'لا',
            })
    elif table_key == 'part_codes':
        qs = qs.select_related('part')
        for p in qs:
            rows.append({
                'sap_code': p.sap_code or '',
                'oracle_code': p.oracle_code or '',
                'part_name': p.part.part_name if p.part else '',
                'part_number': p.part_number or '',
                'manufacturer_co': p.manufacturer_co or '',
                'description': p.description or '',
                'quantity': str(p.quantity or 0),
                'unit_price': str(p.unit_price or 0.0),
                'location': p.location or '',
                'category': p.category or '',
                'unit_of_measure': p.unit_of_measure or '',
            })
    elif table_key == 'shutdowns':
        qs = qs.select_related('factory')
        for s in qs:
            rows.append({
                'name': s.name,
                'factory': s.factory.name if s.factory else '',
                'start_date': s.start_date.isoformat() if s.start_date else '',
                'end_date': s.end_date.isoformat() if s.end_date else '',
            })
    else:
        # Simple lookup tables (Factories, Technicians, ValveTypes, ValveStatuses, Manufacturers)
        for obj in qs:
            rows.append({'name': obj.name})

    # Render as Excel (.xlsx)
    if file_format == 'xlsx':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = spec['name_ar'][:25]
        ws.views.sheetView[0].rightToLeft = True

        header_fill = PatternFill(start_color="004A99", end_color="004A99", fill_type="solid")
        header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Arial", size=10)
        thin_border = Border(
            left=Side(style='thin', color='DEE2E6'),
            right=Side(style='thin', color='DEE2E6'),
            top=Side(style='thin', color='DEE2E6'),
            bottom=Side(style='thin', color='DEE2E6')
        )

        # Write Headers
        for col_idx, col_spec in enumerate(cols, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_spec['key'])
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[1].height = 26

        # Write Data Rows
        for r_idx, row_dict in enumerate(rows, 2):
            for c_idx, col_spec in enumerate(cols, 1):
                k = col_spec['key']
                val = row_dict.get(k, '')
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.font = regular_font
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")

        # Auto-fit widths
        for col in ws.columns:
            max_len = max(len(str(c.value or '')) for c in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        response = HttpResponse(
            buf.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{base_filename}.xlsx"'
        return response

    # Render as CSV
    else:
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="{base_filename}.csv"'

        writer = csv.writer(response)
        # Header keys
        writer.writerow([c['key'] for c in cols])
        for row_dict in rows:
            writer.writerow([row_dict.get(c['key'], '') for c in cols])
        return response


# ==============================================================================
# 3. UNIVERSAL IMPORT ENGINE
# ==============================================================================

def parse_date_safe(val):
    """Safely converts string or date object to datetime.date or None."""
    if not val:
        return None
    if isinstance(val, (datetime, date)):
        return val.date() if isinstance(val, datetime) else val
    val_str = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            pass
    return None


def import_table_data(table_key: str, uploaded_file) -> dict:
    """
    Parses and imports uploaded Excel (.xlsx) or CSV data into the selected table.
    Performs atomic transaction, upserts records, and reports detailed status.
    """
    if table_key not in SUPPORTED_TABLES:
        return {'success': False, 'error': f"الجدول المحدد '{table_key}' غير مدعوم للاستيراد."}

    spec = SUPPORTED_TABLES[table_key]
    model = spec['model']
    cols_spec = spec['columns']
    filename = uploaded_file.name.lower()

    # Read rows
    raw_rows = []
    try:
        if filename.endswith('.xlsx') or filename.endswith('.xlsm'):
            wb = openpyxl.load_workbook(uploaded_file, data_only=True)
            # Pick first sheet or sheet matching table key
            target_sheet = wb.active
            for name in wb.sheetnames:
                if table_key in name.lower():
                    target_sheet = wb[name]
                    break

            rows_iter = target_sheet.iter_rows(values_only=True)
            headers = None
            for row in rows_iter:
                # Find header row
                if not headers:
                    if any(row):
                        headers = [str(c).strip().lower() if c is not None else '' for c in row]
                    continue
                # Skip secondary Arabic header or empty rows
                if not any(row):
                    continue
                # If row looks like description header (contains Arabic), skip
                if any(any('\u0600' <= char <= '\u06FF' for char in str(c)) for c in row if c):
                    # Check if it's the 2nd row header
                    continue
                row_dict = {}
                for idx, h in enumerate(headers):
                    if h and idx < len(row):
                        row_dict[h] = row[idx]
                if any(row_dict.values()):
                    raw_rows.append(row_dict)

        elif filename.endswith('.csv'):
            content = uploaded_file.read().decode('utf-8-sig', errors='ignore')
            reader = csv.DictReader(io.StringIO(content))
            for row in reader:
                clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                if any(clean_row.values()):
                    raw_rows.append(clean_row)
        else:
            return {'success': False, 'error': "صيغة الملف غير مدعومة. يرجى رفع ملف Excel (.xlsx) أو CSV."}

    except Exception as read_err:
        return {'success': False, 'error': f"فشل في قراءة محتوى الملف: {str(read_err)}"}

    if not raw_rows:
        return {'success': False, 'error': "الملف المرفوع فارغ أو لا يحتوي على صفوف بيانات صالحة."}

    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []

    # Execute import in atomic transaction
    try:
        with transaction.atomic():
            for row_num, row in enumerate(raw_rows, start=2):
                try:
                    # 1. VALVES IMPORT
                    if table_key == 'valves':
                        tag = str(row.get('tag_number', '') or '').strip()
                        if not tag:
                            errors.append(f"الصف {row_num}: تم تخطي الصف لعدم وجود كود الصمام (tag_number).")
                            skipped_count += 1
                            continue

                        name = str(row.get('name', '') or tag).strip()
                        location = str(row.get('location', '') or '').strip()
                        factory_str = str(row.get('factory', '') or '').strip()
                        type_str = str(row.get('valve_type', '') or '').strip()
                        status_str = str(row.get('status', '') or '').strip()
                        mfr_str = str(row.get('manufacturer', '') or '').strip()

                        # Resolve ForeignKeys
                        factory = Factory.objects.get_or_create(name=factory_str)[0] if factory_str else None
                        valve_type = ValveType.objects.get_or_create(name=type_str)[0] if type_str else None
                        status = ValveStatus.objects.get_or_create(name=status_str)[0] if status_str else None
                        mfr = Manufacturer.objects.get_or_create(name=mfr_str)[0] if mfr_str else None

                        defaults = {
                            'name': name,
                            'location': location,
                            'factory': factory,
                            'valve_type': valve_type,
                            'status': status,
                            'manufacturer': mfr,
                            'model_number': str(row.get('model_number', '') or '').strip(),
                            'shut_off_pressure': str(row.get('shut_off_pressure', '') or '').strip(),
                            'power_failure_pos': str(row.get('power_failure_pos', '') or '').strip(),
                            'body_style': str(row.get('body_style', '') or '').strip(),
                            'required_travel_angle': str(row.get('required_travel_angle', '') or '').strip(),
                            'bench_range': str(row.get('bench_range', '') or '').strip(),
                            'seat_diameter': str(row.get('seat_diameter', '') or '').strip(),
                            'leakage_class': str(row.get('leakage_class', '') or '').strip(),
                            'installation_date': parse_date_safe(row.get('installation_date')),
                            'last_maintenance_date': parse_date_safe(row.get('last_maintenance_date')),
                            'notes': str(row.get('notes', '') or '').strip(),
                        }

                        obj, created = Valve.objects.update_or_create(tag_number=tag, defaults=defaults)
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    # 2. MAINTENANCE RECORDS IMPORT
                    elif table_key == 'maintenance':
                        valve_tag = str(row.get('valve_tag', '') or '').strip()
                        m_date = parse_date_safe(row.get('maintenance_date'))
                        if not valve_tag or not m_date:
                            errors.append(f"الصف {row_num}: مطلوب كود الصمام (valve_tag) وتاريخ الصيانة (maintenance_date).")
                            skipped_count += 1
                            continue

                        valve = Valve.objects.filter(tag_number__iexact=valve_tag).first()
                        if not valve:
                            # Create placeholder valve if not existing
                            valve = Valve.objects.create(tag_number=valve_tag, name=f"Valve {valve_tag}", location="Imported")

                        tech_str = str(row.get('technician_name', '') or '').strip()
                        tech = Technician.objects.get_or_create(name=tech_str)[0] if tech_str else None

                        is_shut = str(row.get('is_shutdown', '') or '').lower() in ['نعم', 'true', '1', 'yes']

                        raw_press = row.get('testing_pressure')
                        testing_pressure = None
                        if raw_press:
                            try:
                                testing_pressure = float(raw_press)
                            except (ValueError, TypeError):
                                pass

                        defaults = {
                            'technician': tech,
                            'oracle_code': str(row.get('oracle_code', '') or '').strip(),
                            'maintenance_activities': str(row.get('maintenance_activities', '') or '').strip(),
                            'maintenance_notes': str(row.get('maintenance_notes', '') or '').strip(),
                            'pressure_test': str(row.get('pressure_test', '') or '').strip(),
                            'testing_pressure': testing_pressure,
                            'is_shutdown': is_shut,
                        }

                        obj, created = MaintenanceHistory.objects.update_or_create(
                            valve=valve,
                            maintenance_date=m_date,
                            defaults=defaults
                        )
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    # 3. PART CODES IMPORT
                    elif table_key == 'part_codes':
                        sap_code = str(row.get('sap_code', '') or '').strip()
                        part_name = str(row.get('part_name', '') or '').strip()
                        part_num = str(row.get('part_number', '') or '').strip()

                        if not sap_code and not part_num:
                            errors.append(f"الصف {row_num}: يجب توفير كود ساب (sap_code) أو رقم القطعة (part_number).")
                            skipped_count += 1
                            continue

                        # Resolve SparePart master
                        spare_part = None
                        if part_name:
                            spare_part, _ = SparePart.objects.get_or_create(
                                part_name=part_name,
                                defaults={'part_id': slugify(part_name)[:50] or f"P-{row_num}"}
                            )

                        def float_or_zero(val):
                            try:
                                return float(val) if val is not None and str(val).strip() else 0.0
                            except (ValueError, TypeError):
                                return 0.0

                        defaults = {
                            'oracle_code': str(row.get('oracle_code', '') or '').strip(),
                            'part': spare_part,
                            'part_number': part_num,
                            'manufacturer_co': str(row.get('manufacturer_co', '') or '').strip(),
                            'description': str(row.get('description', '') or '').strip(),
                            'quantity': float_or_zero(row.get('quantity')),
                            'unit_price': float_or_zero(row.get('unit_price')),
                            'location': str(row.get('location', '') or '').strip(),
                            'category': str(row.get('category', '') or '').strip(),
                            'unit_of_measure': str(row.get('unit_of_measure', '') or '').strip(),
                        }

                        lookup = {'sap_code': sap_code} if sap_code else {'part_number': part_num}
                        obj, created = PartCode.objects.update_or_create(**lookup, defaults=defaults)
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    # 4. SIMPLE MASTER TABLES (Factory, Technician, ValveType, ValveStatus, Manufacturer)
                    elif table_key in ['factories', 'technicians', 'valve_types', 'valve_statuses', 'manufacturers']:
                        name = str(row.get('name', '') or '').strip()
                        if not name:
                            skipped_count += 1
                            continue
                        obj, created = model.objects.get_or_create(name=name)
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    # 5. SHUTDOWNS
                    elif table_key == 'shutdowns':
                        name = str(row.get('name', '') or '').strip()
                        s_date = parse_date_safe(row.get('start_date'))
                        e_date = parse_date_safe(row.get('end_date'))
                        if not name or not s_date or not e_date:
                            errors.append(f"الصف {row_num}: اسم العمرة وتواريخ البداية والنهاية مطلوبة.")
                            skipped_count += 1
                            continue

                        factory_str = str(row.get('factory', '') or '').strip()
                        factory = Factory.objects.get_or_create(name=factory_str)[0] if factory_str else None

                        obj, created = Shutdown.objects.update_or_create(
                            name=name,
                            defaults={'factory': factory, 'start_date': s_date, 'end_date': e_date}
                        )
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                except Exception as row_err:
                    errors.append(f"الصف {row_num}: خطأ ({str(row_err)})")
                    skipped_count += 1

    except Exception as tx_err:
        return {'success': False, 'error': f"فشلت عملية الاستيراد: {str(tx_err)}"}

    return {
        'success': True,
        'table_key': table_key,
        'table_name_ar': spec['name_ar'],
        'total_rows': len(raw_rows),
        'created_count': created_count,
        'updated_count': updated_count,
        'skipped_count': skipped_count,
        'errors': errors[:50],  # Return up to 50 errors for user visibility
    }

