from django.test import TestCase
from valves.models import Valve, MaintenanceHistory, PartCode, Technician
from django.utils import timezone

class ValveRelatedNameTest(TestCase):
    def setUp(self):
        self.valve = Valve.objects.create(
            tag_number="TEST-001",
            name="Test Valve"
        )
        self.maintenance = MaintenanceHistory.objects.create(
            valve=self.valve,
            maintenance_date=timezone.now().date()
        )
        self.part_code = PartCode.objects.create(
            sap_code="SAP-001"
        )
        self.part_code.associated_valves.add(self.valve)

    def test_maintenance_records_related_name(self):
        """Test that maintenance_records related name works"""
        self.assertTrue(hasattr(self.valve, 'maintenance_records'))
        self.assertEqual(self.valve.maintenance_records.count(), 1)
        self.assertEqual(self.valve.maintenance_records.first(), self.maintenance)

    def test_part_codes_related_name(self):
        """Test that part_codes related name works"""
        self.assertTrue(hasattr(self.valve, 'part_codes'))
        self.assertEqual(self.valve.part_codes.count(), 1)
        self.assertEqual(self.valve.part_codes.first(), self.part_code)

    def test_technical_specs_fields(self):
        """Test that new technical spec fields exist and can store values"""
        self.valve.plug_stem_mat = "316SS"
        self.valve.packing_mat = "Graphite"
        self.valve.shut_off_pressure = "10 BAR"
        self.valve.save()
        
        db_valve = Valve.objects.get(tag_number="TEST-001")
        self.assertEqual(db_valve.plug_stem_mat, "316SS")
        self.assertEqual(db_valve.packing_mat, "Graphite")
        self.assertEqual(db_valve.shut_off_pressure, "10 BAR")

from valves.forms import MaintenanceHistoryForm
from valves.models import Shutdown, Factory

class MaintenanceShutdownTest(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="AFC I")
        self.valve = Valve.objects.create(
            tag_number="SHUTDOWN-VALVE",
            name="Shutdown Test Valve",
            factory=self.factory
        )
        self.technician = Technician.objects.create(name="Test Tech")

    def test_shutdown_creation_on_save(self):
        """Test that checking is_shutdown in the form creates a Shutdown record"""
        form_data = {
            'valve_tag_number': 'SHUTDOWN-VALVE',
            'technician_name': 'Test Tech',
            'maintenance_date': '2026-05-15',
            'is_shutdown': True,
            'maintenance_activities': ['On site'],
        }
        
        form = MaintenanceHistoryForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        
        # Check if Shutdown record was created
        shutdowns = Shutdown.objects.filter(factory=self.factory, name="May 2026")
        self.assertEqual(shutdowns.count(), 1)
        
        shutdown = shutdowns.first()
        self.assertEqual(shutdown.start_date.year, 2026)
        self.assertEqual(shutdown.start_date.month, 5)
        self.assertEqual(shutdown.start_date.day, 1)
        self.assertTrue(self.valve in shutdown.valves.all())

