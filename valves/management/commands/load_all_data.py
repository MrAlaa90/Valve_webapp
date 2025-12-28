from django.core.management.base import BaseCommand
from django.core import management
from valves.scripts import data_loader, part_code_loader

class Command(BaseCommand):
    help = 'Loads all data from CSV files.'

    def handle(self, *args, **options):
        self.stdout.write('Starting all data loading...')

        self.stdout.write('Step 1: Populating lookup tables...')
        management.call_command('populate_lookups')
        self.stdout.write(self.style.SUCCESS('Finished populating lookup tables.'))

        self.stdout.write('Step 2: Loading new valves from valves_data.csv...')
        management.call_command('load_new_valves')
        self.stdout.write(self.style.SUCCESS('Finished loading new valves.'))

        self.stdout.write('Step 3: Loading valve data from AFC CSV files...')
        data_loader.run()
        self.stdout.write(self.style.SUCCESS('Finished loading AFC valve data.'))

        self.stdout.write('Step 4: Loading part code data...')
        part_code_loader.run()
        self.stdout.write(self.style.SUCCESS('Finished loading part code data.'))

        self.stdout.write(self.style.SUCCESS('All data loading commands executed successfully!'))
