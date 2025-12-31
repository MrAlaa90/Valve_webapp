from django.core.management.base import BaseCommand
from valves.scripts import part_code_loader

class Command(BaseCommand):
    help = 'Loads part code data from CSV files.'

    def handle(self, *args, **options):
        self.stdout.write('Starting part code data import...')
        part_code_loader.run()
        self.stdout.write(self.style.SUCCESS('Successfully finished importing part code data.'))
