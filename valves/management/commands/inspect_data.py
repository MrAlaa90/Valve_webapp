from django.core.management.base import BaseCommand
from valves.models import Valve, PartCode, Factory
from django.db.models import Count

class Command(BaseCommand):
    help = 'Inspects the data in the database after loading.'

    def handle(self, *args, **options):
        self.stdout.write('Starting data inspection...')

        # 1. Count Valve and PartCode objects
        valve_count = Valve.objects.count()
        part_code_count = PartCode.objects.count()
        self.stdout.write(f'Total Valves in DB: {valve_count}')
        self.stdout.write(f'Total PartCodes in DB: {part_code_count}')

        # 2. Inspect sample valves
        self.stdout.write('\n--- Inspecting Sample Valves ---')
        
        valves_to_inspect = {
            "AFC I": "FV-33001",
            "AFC II": "AV-21707",
            "AFC III": "AV-335701"
        }

        for factory_name, tag_number in valves_to_inspect.items():
            self.stdout.write(f'\n--- Checking {factory_name} Valve: {tag_number} ---')
            try:
                valve = Valve.objects.get(tag_number=tag_number)
                self.stdout.write(f'  Tag Number: {valve.tag_number}')
                self.stdout.write(f'  Factory: {valve.factory.name if valve.factory else "N/A"}')
                self.stdout.write(f'  Manufacturer: {valve.manufacturer.name if valve.manufacturer else "N/A"}')
                self.stdout.write(f'  Model Number: {valve.model_number if valve.model_number else "N/A"}')
                self.stdout.write(f'  Shut-off Pressure: {valve.shut_off_pressure if valve.shut_off_pressure else "N/A"}')
            except Valve.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Valve {tag_number} not found in the database.'))

        # 3. Inspect a PartCode and its associations
        self.stdout.write('\n--- Inspecting PartCode Associations ---')
        try:
            # Using a part code that has a tag number in the CSV
            part_code = PartCode.objects.get(sap_code='0190336800030024') # This one is linked to HV-33401
            self.stdout.write(f'Found PartCode: {part_code.sap_code} ({part_code.description})')
            associated_valves = part_code.associated_valves.all()
            if associated_valves:
                self.stdout.write('  Associated Valves:')
                for valve in associated_valves:
                    self.stdout.write(f'    - {valve.tag_number}')
            else:
                self.stdout.write('  No valves associated with this part code.')
        except PartCode.DoesNotExist:
            self.stdout.write(self.style.WARNING('Could not find the sample PartCode to inspect.'))
            
        self.stdout.write('\nInspection complete.')
