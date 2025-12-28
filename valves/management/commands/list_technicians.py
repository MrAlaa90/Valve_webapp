from django.core.management.base import BaseCommand
from valves.models import Technician

class Command(BaseCommand):
    help = 'Lists all technicians in the database.'

    def handle(self, *args, **options):
        self.stdout.write('--- Technicians in Database ---')
        technicians = Technician.objects.all()
        if technicians:
            for tech in technicians:
                self.stdout.write(f'- {tech.name}')
        else:
            self.stdout.write('No technicians found.')
        self.stdout.write('--- End of List ---')
