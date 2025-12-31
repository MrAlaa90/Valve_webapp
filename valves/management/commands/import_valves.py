from django.core.management.base import BaseCommand
from valves.scripts import data_loader

class Command(BaseCommand):
    help = 'Loads valve data from CSV files.'

    def handle(self, *args, **options):
        self.stdout.write('Starting valve data import...')
        data_loader.run()
        self.stdout.write(self.style.SUCCESS('Successfully finished importing valve data.'))
