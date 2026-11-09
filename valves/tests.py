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


import tempfile
import shutil
from pathlib import Path
from django.db import connection
from django.urls import reverse
import backup_manager
from desktop_app.paths import get_default_data_dir


class DesktopPragmasTest(TestCase):
    def test_sqlite_enterprise_pragmas(self):
        """Verifies SQLite enterprise pragmas are applied on active connection"""
        if connection.vendor == 'sqlite':
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys;")
            fk = cursor.fetchone()[0]
            self.assertEqual(fk, 1)

            cursor.execute("PRAGMA busy_timeout;")
            timeout = cursor.fetchone()[0]
            self.assertEqual(timeout, 10000)
            cursor.close()


class BackupEngineAndViewsTest(TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / "data"
        self.backup_dir = self.test_dir / "backups"
        self.data_dir.mkdir(parents=True)
        self.backup_dir.mkdir(parents=True)

        # Create dummy db file and media
        self.db_file = self.data_dir / "db.sqlite3"
        import sqlite3
        conn = sqlite3.connect(self.db_file)
        conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);")
        conn.execute("INSERT INTO test_table (name) VALUES ('Test Valve');")
        conn.commit()
        conn.close()

        self.media_file = self.data_dir / "media" / "test.txt"
        self.media_file.parent.mkdir(parents=True)
        self.media_file.write_text("dummy media content")

        self.engine = backup_manager.GFSBackupEngine(
            data_dir=self.data_dir,
            backup_dir=self.backup_dir
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_and_verify_backup(self):
        """Test atomic backup creation and SHA-256 verification"""
        res = self.engine.create_backup(backup_type="manual", note="Unit test backup")
        self.assertTrue(res.get("success"))
        archive_path = Path(res["archive_path"])
        self.assertTrue(archive_path.exists())

        # Check sha256 file
        sha_file = archive_path.parent / f"{archive_path.name}.sha256"
        self.assertTrue(sha_file.exists())

        # Verify integrity
        verify_res = self.engine.verify_backup(archive_path)
        self.assertTrue(verify_res.get("valid"))
        self.assertEqual(verify_res.get("sha256"), res["checksum"])

    def test_backup_management_view(self):
        """Test that the /backups/ dashboard view renders with 200 OK"""
        response = self.client.get(reverse('valves:backup-management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enterprise Backup & Disaster Recovery")


