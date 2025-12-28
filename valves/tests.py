from django.test import TestCase
from valves.models import Valve, MaintenanceHistory, PartCode
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
