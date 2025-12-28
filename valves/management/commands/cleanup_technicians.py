from django.core.management.base import BaseCommand
from valves.models import Technician

class Command(BaseCommand):
    help = 'Removes specified technicians from the database.'

    def handle(self, *args, **options):
        technicians_to_remove = ["ahmed", "mohamed", "ali"]
        
        self.stdout.write("Removing old technicians...")
        
        deleted_count, _ = Technician.objects.filter(name__in=technicians_to_remove).delete()
        
        self.stdout.write(self.style.SUCCESS(f"Successfully removed {deleted_count} old technicians."))
