import csv
import os
from pathlib import Path
from django.db import IntegrityError, transaction

from valves import models

# تحديد المسار الأساسي للمشروع ومسار ملف CSV
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_FILE_NAME = 'part_codes_data.csv'
CSV_FILE_PATH = os.path.join(BASE_DIR, 'valves', CSV_FILE_NAME)

def run():
    """
    Loads PartCode and SparePart data from a CSV file into the database.
    """
    print(f"--- Starting part codes import from: {CSV_FILE_PATH} ---")

    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: File {CSV_FILE_NAME} not found at the expected path.")
        print("Please make sure the file is inside the 'valves' folder.")
        return

    DELIMITER = ','

    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=DELIMITER)

            if not reader.fieldnames:
                print(f"Error: No column headers found in the file (using delimiter '{DELIMITER}').")
                return

            print(f"Columns found: {reader.fieldnames}")

            rows_processed = 0
            parts_created = 0
            codes_created = 0
            codes_updated = 0
            rows_skipped = 0
            associations_made = 0

            # Use @transaction.atomic to ensure the save process is done in one batch
            with transaction.atomic():
                for row in reader:
                    rows_processed += 1

                    # Clean data from extra spaces
                    data = {k.strip(): v.strip() for k, v in row.items() if k}

                    # Extract basic data
                    part_number = data.get('part_number')
                    sap_code = data.get('sap_code')
                    description = data.get('description')
                    tag_number_string = data.get('tag_number')

                    # 1. Check for essential data
                    if not sap_code:
                        print(f"Warning: Skipping row {rows_processed} due to missing 'sap_code': {row}")
                        rows_skipped += 1
                        continue

                    # We will use sap_code as a unique identifier for PartCode and SparePart
                    # This ensures no data duplication when re-running the script
                    code_id = sap_code
                    part_id_identifier = sap_code

                    # 2. Find or create SparePart
                    try:
                        spare_part, created = models.SparePart.objects.get_or_create(
                            part_id=part_id_identifier,
                            defaults={
                                'part_name': description or f'Spare Part: {part_id_identifier}',
                            }
                        )
                        if created:
                            parts_created += 1

                    except Exception as e:
                        print(f"Error creating/finding SparePart for row {rows_processed} ({part_id_identifier}): {e}, Row: {row}")
                        rows_skipped += 1
                        continue

                    # 3. Create or update PartCode
                    try:
                        part_code, created = models.PartCode.objects.update_or_create(
                            code_id=code_id,
                            defaults={
                                'part': spare_part,
                                'warehouse_number': data.get('warehouse_number', 'N/A'),
                                'sap_code': sap_code,
                                'oracle_code': data.get('oracle_code'),
                                'condition': data.get('condition', 'New'),
                                'description': description,
                                'part_number': part_number,
                                'unit_of_measure': data.get('unit_of_measure', 'Unit'),
                                'category': data.get('category', 'Uncategorized'),                                
                                'MANUFATURE_CO': data.get('MANUFATURE_CO'),
                                'quantity': 0,  # No quantity field in the file, so we set a default value
                            }
                        )

                        # 4. معالجة وربط البلوف المرتبطة (Associated Valves)
                        if tag_number_string:
                            # تنظيف وتجهيز قائمة التاجات
                            # يستبدل "/" بـ "," ثم يقسم النص للحصول على قائمة
                            cleaned_tags = [tag.strip() for tag in tag_number_string.replace('/', ',').split(',') if tag.strip()]
                            
                            if cleaned_tags:
                                # البحث عن كل البلوف التي تطابق التاجات الموجودة في القائمة
                                valves_to_associate = models.Valve.objects.filter(tag_number__in=cleaned_tags)
                                
                                if valves_to_associate.exists():
                                    # استخدام .set() لربط البلوف بكود القطعة
                                    # هذه الدالة تقوم بمسح العلاقات القديمة وإضافة الجديدة بكفاءة
                                    part_code.associated_valves.set(valves_to_associate)
                                    associations_made += 1

                        if created:
                            codes_created += 1
                        else:
                            codes_updated += 1

                    except IntegrityError as ie:
                        print(f"Integrity error for row {rows_processed}: {ie}")
                        rows_skipped += 1
                    except Exception as e:
                        print(f"Error creating/updating PartCode for row {rows_processed} ({code_id}): {e}")
                        rows_skipped += 1

            # Outside transaction.atomic()
            print("-------------------------------------------------------")
            print("Import process completed successfully (processed in a single transaction).")
            print(f"Total rows processed: {rows_processed}")
            print(f"Total rows skipped due to errors: {rows_skipped}")
            print(f"Total new spare parts created (SparePart): {parts_created}")
            print(f"Total new part codes created (PartCode): {codes_created}")
            print(f"Total part codes with valve associations processed: {associations_made}")
            print(f"Total part codes updated (PartCode): {codes_updated}")
            print("-------------------------------------------------------")

    except Exception as e:
        print(f"A general error occurred while processing the file (transaction rolled back): {e}")
    print("--- Finished part codes import ---")
