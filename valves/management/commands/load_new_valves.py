from django.core.management.base import BaseCommand
from valves.scripts import new_data_loader

class Command(BaseCommand):
    help = 'Loads valve data from valves/valves_data.csv'

    def handle(self, *args, **options):
        self.stdout.write('Starting to load new valve data...')
        new_data_loader.run()
        self.stdout.write(self.style.SUCCESS('Successfully finished loading new valve data.'))
