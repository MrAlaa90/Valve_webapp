import csv
import os
from valves.models import PartCode, SparePart, Valve

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_part_code_importer():
    """
    Loads part code data from part_codes_data.csv into the database.
    """
    part_codes_csv = os.path.join(BASE_DIR, '..', 'part_codes_data.csv')
    try:
        with open(part_codes_csv, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    if not row['sap_code']:
                        continue

                    # Create or get SparePart
                    spare_part = None
                    if row['part_number']:
                        spare_part, created = SparePart.objects.get_or_create(
                            part_id=row['part_number'],
                            defaults={'part_name': row['description']}
                        )

                    # Create or update PartCode
                    part_code, created = PartCode.objects.update_or_create(
                        sap_code=row['sap_code'],
                        defaults={
                            'oracle_code': row['oracle_code'],
                            'part': spare_part,
                            'description': row['description'],
                            'location': row['warehouse_number'],
                            'category': row['category'],
                            'condition': row['condition'],
                            'part_number': row['part_number'],
                            'manufacturer_co': row['MANUFATURE_CO'],
                            'unit_of_measure': row['unit_of_measure'],
                        }
                    )

                    # Associate with valve
                    if row['tag_number']:
                        def format_tag_number(tag):
                            # Remove spaces and convert to uppercase
                            tag = tag.replace(' ', '').upper()
                            # Add hyphen after the first two letters if followed by numbers
                            if len(tag) > 2 and tag[0:2].isalpha() and tag[2:].isdigit():
                                tag = f"{tag[0:2]}-{tag[2:]}"
                            return tag

                        # Normalize tag_number: replace commas with slashes, then format each tag
                        cleaned_tag_numbers_str = row['tag_number'].replace(',', '/')
                        tag_numbers = [format_tag_number(tag.strip()) for tag in cleaned_tag_numbers_str.split('/')]
                        for tag_number in tag_numbers:
                            try:
                                valve = Valve.objects.get(tag_number__iexact=tag_number) # Use iexact for case-insensitive matching
                                part_code.associated_valves.add(valve)
                            except Valve.DoesNotExist:
                                print(f"Valve with tag number {tag_number} not found.")

                except Exception as e:
                    print(f"Error processing row: {row}. Error: {e}")
                    continue
        print("Successfully imported part codes.")
    except FileNotFoundError:
        print(f"Error: {part_codes_csv} not found.")
    except Exception as e:
        print(f"An error occurred while importing part codes: {e}")

def run():
    run_part_code_importer()