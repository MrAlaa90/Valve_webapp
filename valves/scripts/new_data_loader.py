import csv
import os
from valves.models import Valve

def run_new_data_loader():
    """
    Loads valve data from valves/valves_data.csv into the database.
    It uses update_or_create to update existing valves or create new ones based on tag_number.
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'valves_data.csv')

    updated_count = 0
    created_count = 0

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row

            for row in reader:
                if not row:
                    continue
                tag_number = row[0].strip()
                if not tag_number:
                    continue

                obj, created = Valve.objects.update_or_create(
                    tag_number=tag_number,
                    defaults={'name': f"Valve {tag_number}"} 
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        print(f"Finished processing {file_path}.")
        print(f"Created: {created_count}, Updated: {updated_count}")

    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def run():
    run_new_data_loader()
