import sqlite3
from django.test import TestCase
from django.contrib.auth.models import User
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


class UserManagementTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            password="adminpassword123",
            email="admin@test.com"
        )
        self.normal_user = User.objects.create_user(
            username="normal_test",
            password="normalpassword123",
            email="normal@test.com"
        )
        self.factory = Factory.objects.create(name="AFC II")
        self.technician = Technician.objects.create(name="Tarek Tech")

    def test_user_list_requires_admin(self):
        # Anonymous user redirected to login
        resp = self.client.get(reverse('valves:user-list'))
        self.assertEqual(resp.status_code, 302)

        # Normal user redirected with error
        self.client.login(username="normal_test", password="normalpassword123")
        resp = self.client.get(reverse('valves:user-list'))
        self.assertEqual(resp.status_code, 302)

        # Admin user gets 200 OK
        self.client.login(username="admin_test", password="adminpassword123")
        resp = self.client.get(reverse('valves:user-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "admin_test")
        self.assertContains(resp, "normal_test")

    def test_user_create_by_admin(self):
        self.client.login(username="admin_test", password="adminpassword123")
        post_data = {
            'username': 'new_technician',
            'first_name': 'Ali',
            'last_name': 'Hassan',
            'email': 'ali@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'technician',
            'factory': self.factory.pk,
            'technician': self.technician.pk,
            'is_active': True,
        }
        resp = self.client.post(reverse('valves:user-create'), data=post_data)
        self.assertEqual(resp.status_code, 302)

        # Verify user created with profile
        new_user = User.objects.get(username='new_technician')
        self.assertEqual(new_user.first_name, 'Ali')
        self.assertEqual(new_user.profile.role, 'technician')
        self.assertEqual(new_user.profile.factory, self.factory)
        self.assertEqual(new_user.profile.technician, self.technician)

    def test_user_cannot_delete_self(self):
        self.client.login(username="admin_test", password="adminpassword123")
        # Attempt to delete self
        resp = self.client.post(reverse('valves:user-delete', kwargs={'pk': self.admin_user.pk}))
        self.assertEqual(resp.status_code, 302)
        # Verify self still exists
        self.assertTrue(User.objects.filter(pk=self.admin_user.pk).exists())

    def test_user_detail_view(self):
        self.client.login(username="admin_test", password="adminpassword123")
        resp = self.client.get(reverse('valves:user-detail', kwargs={'pk': self.normal_user.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "normal_test")
        self.assertContains(resp, "الصلاحيات")


class DailyBackupStrictRetentionTest(TestCase):
    """
    Verifies that daily backups enforce a strict 7-day rolling window:
    On the 8th daily backup, the 1st backup from the previous week is deleted,
    and exactly 7 daily backups remain.
    """
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "db.sqlite3"
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE test_data (id INT);")
        conn.commit()
        conn.close()

        self.backup_dir = self.temp_dir / "backups"
        self.engine = backup_manager.GFSBackupEngine(
            data_dir=self.temp_dir,
            backup_dir=self.backup_dir
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_eight_daily_backups_prune_oldest_leaving_seven(self):
        import time
        created_archives = []

        # Create 8 consecutive daily backups
        for day in range(1, 9):
            res = self.engine.create_backup(backup_type="daily", note=f"Daily backup day {day}")
            self.assertTrue(res["success"])
            created_archives.append(res["filename"])
            time.sleep(0.05)  # slight pause so timestamps differ

        daily_backups = [b for b in self.engine.list_backups() if b["category"] == "daily"]

        # Exactly 7 daily backups must remain
        self.assertEqual(len(daily_backups), 7)

        # The 1st created archive must have been deleted
        remaining_filenames = [b["filename"] for b in daily_backups]
        self.assertNotIn(created_archives[0], remaining_filenames, "Oldest day 1 backup must be deleted on day 8")
        # The 8th (latest) must be present
        self.assertIn(created_archives[-1], remaining_filenames, "Newest day 8 backup must be present")


from valves.data_exchange import (
    generate_excel_templates_workbook,
    export_table_to_response,
    import_table_data,
    SUPPORTED_TABLES
)
import io
from django.core.files.uploadedfile import SimpleUploadedFile


class DataExchangeTest(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="AFC I")
        self.valve = Valve.objects.create(
            tag_number="EXCH-001",
            name="Data Exchange Valve",
            factory=self.factory
        )
        self.admin = User.objects.create_superuser("admin_exch", "admin@exch.com", "pass123")
        self.viewer = User.objects.create_user("viewer_exch", "viewer@exch.com", "pass123")
        self.viewer.profile.role = 'viewer'
        self.viewer.profile.can_export = False
        self.viewer.profile.can_import = False
        self.viewer.profile.save()

    def test_excel_templates_generation(self):
        """Test multi-sheet templates workbook generator"""
        wb_bytes = generate_excel_templates_workbook()
        self.assertTrue(len(wb_bytes) > 5000)

    def test_export_table_xlsx_and_csv(self):
        """Test export to Excel and CSV responses"""
        resp_xlsx = export_table_to_response('valves', file_format='xlsx')
        self.assertEqual(resp_xlsx.status_code, 200)
        self.assertEqual(resp_xlsx['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        resp_csv = export_table_to_response('valves', file_format='csv')
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertIn(b"EXCH-001", resp_csv.content)

    def test_import_valves_from_csv(self):
        """Test importing valves from a CSV file"""
        csv_data = (
            "tag_number,name,location,factory,valve_type,status\n"
            "IMP-001,Imported Valve 1,Unit 10,AFC I,Globe,Operational\n"
            "IMP-002,Imported Valve 2,Unit 20,AFC II,Ball,Operational\n"
        ).encode('utf-8')

        uploaded = SimpleUploadedFile("valves_test.csv", csv_data, content_type="text/csv")
        result = import_table_data('valves', uploaded)

        self.assertTrue(result['success'])
        self.assertEqual(result['created_count'], 2)
        self.assertTrue(Valve.objects.filter(tag_number="IMP-001").exists())
        self.assertTrue(Valve.objects.filter(tag_number="IMP-002").exists())

    def test_dashboard_access_permissions(self):
        """Test data exchange access permissions"""
        # Viewer with can_export=False, can_import=False is blocked
        self.client.login(username="viewer_exch", password="pass123")
        resp = self.client.get(reverse('valves:data-exchange'))
        self.assertEqual(resp.status_code, 302)

        # Admin gets 200 OK
        self.client.login(username="admin_exch", password="pass123")
        resp = self.client.get(reverse('valves:data-exchange'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "مركز استيراد وتصدير البيانات")




