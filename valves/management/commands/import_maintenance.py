import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from valves.models import Valve, Technician, MaintenanceHistory, Factory

class Command(BaseCommand):
    help = 'Import maintenance history from a CSV file'

    def handle(self, *args, **kwargs):
        csv_file_path = 'extracted_data.csv'
        self.stdout.write(f"Starting import from {csv_file_path}")

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    tag_number = row.get('Tag_Number', '').strip()
                    if not tag_number:
                        self.stdout.write(self.style.WARNING(f"Skipping row due to empty Tag_Number: {row}"))
                        continue

                    try:
                        valve = Valve.objects.get(tag_number=tag_number)
                    except Valve.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Valve with tag_number '{tag_number}' not found. Skipping row: {row}"))
                        continue

                    # Date parsing
                    date_str = row.get('Date', '').strip()
                    maintenance_date = None
                    if date_str:
                        possible_formats = ['%d-%m-%Y', '%d/%m/%Y %H:%M', '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%Y %H:%M']
                        for fmt in possible_formats:
                            try:
                                maintenance_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                pass
                        if not maintenance_date:
                            self.stdout.write(self.style.WARNING(f"Could not parse date '{date_str}' for valve '{tag_number}'. Skipping date."))
                    
                    if not maintenance_date:
                        self.stdout.write(self.style.WARNING(f"Skipping maintenance record for '{tag_number}' due to missing or invalid date."))
                        continue

                    # Technician
                    technician_name = row.get('Technician', '').strip()
                    technician = None
                    if technician_name:
                        technician, created = Technician.objects.get_or_create(name=technician_name)
                        if created:
                            self.stdout.write(f"Created new technician: {technician_name}")

                    # Maintenance Activities/Notes
                    work_done = row.get('Work_Done', '').strip()
                    test_info = row.get('Test', '').strip()
                    
                    maintenance_notes = work_done
                    if test_info:
                        maintenance_notes = f"{work_done}\nTest: {test_info}"

                    # Create or update MaintenanceHistory record
                    obj, created = MaintenanceHistory.objects.update_or_create(
                        valve=valve,
                        maintenance_date=maintenance_date,
                        defaults={
                            'maintenance_notes': maintenance_notes,
                            'technician': technician,
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created new maintenance record for valve '{tag_number}' on {maintenance_date}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Updated existing maintenance record for valve '{tag_number}' on {maintenance_date}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))

        self.stdout.write(self.style.SUCCESS("Import completed."))
