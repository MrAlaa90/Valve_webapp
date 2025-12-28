from django.core.management.base import BaseCommand
from valves.models import ValveType, ValveStatus, Manufacturer, Technician

class Command(BaseCommand):
    help = 'Populates initial lookup data for ValveType, ValveStatus, Manufacturer, and Technician.'

    def handle(self, *args, **options):
        self.stdout.write("Populating lookup tables...")

        # Populate ValveType
        valve_types = ["Globe Valve", "Ball Valve", "Butterfly Valve", "Diaphragm Valve", "Gate Valve", "Check Valve", "Plug Valve", "Angle Valve", "Piston"]
        for vt_name in valve_types:
            ValveType.objects.get_or_create(name=vt_name)
        self.stdout.write(self.style.SUCCESS(f"Populated {len(valve_types)} Valve Types."))

        # Populate ValveStatus
        valve_statuses = ["Good", "Fair", "Needs Maintenance", "Out of Service", "Operational"]
        for vs_name in valve_statuses:
            ValveStatus.objects.get_or_create(name=vs_name)
        self.stdout.write(self.style.SUCCESS(f"Populated {len(valve_statuses)} Valve Statuses."))

        # Populate Manufacturers (add some common ones or leave empty for CSV to populate)
        manufacturers = ["FISHER-GULDE", "NELES", "UHDE", "BABCOCK", "XOMOX", "URACA", "COPES-VULKON", "NORVIK YORWOY", "STI", "BOMAFA", "DECARDEN", "HANEYWEEL", "EMERSON PROCESS", "GOLDE"]
        for m_name in manufacturers:
            Manufacturer.objects.get_or_create(name=m_name)
        self.stdout.write(self.style.SUCCESS(f"Populated {len(manufacturers)} Manufacturers."))

        # Populate Technicians (add some common ones or leave empty for data migration to populate)
        technicians = ["M.Saad", "M.Abd Allah", "M.Gomaa", "ALAA", "A.Salah"]
        for t_name in technicians:
            Technician.objects.get_or_create(name=t_name)
        self.stdout.write(self.style.SUCCESS(f"Populated {len(technicians)} Technicians."))

        self.stdout.write(self.style.SUCCESS("Lookup tables populated successfully!"))
