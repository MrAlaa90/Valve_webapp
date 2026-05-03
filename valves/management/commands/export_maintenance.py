import csv
from django.core.management.base import BaseCommand
from valves.models import MaintenanceHistory

class Command(BaseCommand):
    help = 'Export maintenance history to a CSV file'

    def handle(self, *args, **kwargs):
        output_file = 'extracted_data_updated.csv'
        records = MaintenanceHistory.objects.all().select_related('valve', 'technician')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Factory', 'Tag_Number', 'Date', 'Work_Done', 'Test', 'Technician'])
            
            for r in records:
                factory = r.valve.factory.name if r.valve.factory else ''
                tag = r.valve.tag_number
                date = r.maintenance_date.strftime('%d-%m-%Y')
                
                # Split notes if they contain "Test:"
                notes = r.maintenance_notes or ''
                work_done = notes
                test = ''
                if 'Test:' in notes:
                    parts = notes.split('Test:')
                    work_done = parts[0].strip()
                    test = parts[1].strip()
                
                tech = r.technician.name if r.technician else ''
                
                writer.writerow([factory, tag, date, work_done, test, tech])
        
        self.stdout.write(self.style.SUCCESS(f'Successfully exported {records.count()} records to {output_file}'))
