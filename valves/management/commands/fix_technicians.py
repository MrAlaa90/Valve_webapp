
from django.core.management.base import BaseCommand
from valves.models import MaintenanceHistory, Technician

class Command(BaseCommand):
    help = 'Fixes technician foreign key constraint errors.'

    def handle(self, *args, **options):
        self.stdout.write('Starting technician fix...')
        technician_names = MaintenanceHistory.objects.values_list('technician_name', flat=True).distinct()
        for name in technician_names:
            if name:
                technician, created = Technician.objects.get_or_create(name=name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created technician: {name}'))
        self.stdout.write(self.style.SUCCESS('Finished technician fix.'))
