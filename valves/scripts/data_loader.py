import csv
import glob
import os
from valves.models import Valve, ValveType, ValveStatus, Manufacturer, Factory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_valve_importer():
    """
    Loads valve data from CSV files in the valves/valves_db/ directory into the database.
    The script extracts the factory name from the CSV filename.
    It uses update_or_create to update existing valves or create new ones.
    """
    
    db_dir = os.path.join(BASE_DIR, '..', 'valves_db')
    csv_files = glob.glob(os.path.join(db_dir, '*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in {db_dir}")
        return

    print(f"Found {len(csv_files)} CSV files to process.")

    total_updated_count = 0
    total_created_count = 0

    for csv_file_path in csv_files:
        factory_name_from_file = os.path.basename(csv_file_path).split('.')[0].split('_')[0]
        factory_name_map = {
            'AFC1': 'AFC I',
            'AFC2': 'AFC II',
            'AFC3': 'AFC III',
        }
        factory_name = factory_name_map.get(factory_name_from_file, factory_name_from_file)
        print(f"Processing file: {csv_file_path} for factory: {factory_name}")

        updated_count = 0
        created_count = 0

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                # Use DictReader for easier column access by name
                reader = csv.DictReader(file)
                # Clean fieldnames once to handle potential BOM or extra spaces in headers
                # This ensures that subsequent row.get() calls use clean keys
                reader.fieldnames = [field.strip().replace('\ufeff', '') for field in reader.fieldnames]
                
                for row in reader:
                    try:
                        if not row: # Skip empty rows
                            continue
                        # Create a new dictionary with cleaned keys and values for robust access
                        cleaned_row = {k.strip(): v.strip() for k, v in row.items() if k is not None}
                        


                        tag_number = cleaned_row.get('tag_number')
                        if not tag_number:
                            continue
                        

                        

                        
                        manufacturer = None
                        model_number = None
                        manufacturer_model = cleaned_row.get('Manufacturer / Model')
                        if manufacturer_model:
                            parts = manufacturer_model.split('/')
                            if len(parts) > 1:
                                manufacturer = parts[0].strip()
                                model_number = parts[1].strip()
                            else:
                                manufacturer = parts[0].strip()

                        valve_data = {
                            'factory': Factory.objects.get_or_create(name=factory_name)[0],
                            'name': f"Valve {tag_number}",
                            'location': "Not specified",
                            'valve_type': ValveType.objects.get_or_create(name="General")[0],
                            'status': ValveStatus.objects.get_or_create(name="Operational")[0],
                            'manufacturer': Manufacturer.objects.get_or_create(name=manufacturer)[0] if manufacturer else None,
                            'model_number': model_number,
                            'shut_off_pressure': cleaned_row.get('Shut-off Pressures P1 / P2') or None,
                            'power_failure_pos': cleaned_row.get('Power Failure Pos.') or None,
                            'body_style': cleaned_row.get('Body Style') or None,
                            'required_travel_angle': cleaned_row.get('Required Travel / Angle') or None,
                            'bench_range': cleaned_row.get('Bench Range') or None,
                        }
                        
                        obj, created = Valve.objects.update_or_create(
                            tag_number=tag_number,
                            defaults=valve_data
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    except Exception as e:
                        print(f"Error processing row: {row}. Error: {e}")
                        continue
            print(f"Finished processing {csv_file_path}.")
            print(f"Created: {created_count}, Updated: {updated_count}")
            total_created_count += created_count
            total_updated_count += updated_count

        except FileNotFoundError:
            print(f"Error: File not found at path: {csv_file_path}")
        except Exception as e:
            print(f"A general error occurred during the process: {e}")

    print("-" * 50)
    print(f"Total new valves created: {total_created_count}")
    print(f"Total existing valves updated: {total_updated_count}")

def update_sort_order():
    """
    Updates the sort_order field for each valve based on its order in the valves_data.csv file.
    """
    valves_data_csv = os.path.join(BASE_DIR, '..', 'valves_data.csv')
    try:
        with open(valves_data_csv, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for i, row in enumerate(reader):
                if row:
                    tag_number = row[0].strip()
                    if tag_number:
                        Valve.objects.filter(tag_number=tag_number).update(sort_order=i)
        print("Successfully updated sort order for valves.")
    except FileNotFoundError:
        print(f"Error: {valves_data_csv} not found.")
    except Exception as e:
        print(f"An error occurred while updating sort order: {e}")

def run():
    run_valve_importer()
    update_sort_order()