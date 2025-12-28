import os
import re
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from valves.models import Valve, ValveImage

class Command(BaseCommand):
    help = 'Links existing image files in the assets directory to Valve objects.'

    def handle(self, *args, **options):
        self.stdout.write("Linking valve images...")

        base_assets_dir = os.path.join(settings.BASE_DIR, 'assets')
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
        linked_count = 0
        skipped_count = 0

        for root, _, files in os.walk(base_assets_dir):
            for file_name in files:
                if file_name.lower().endswith(image_extensions):
                    full_path = os.path.join(root, file_name)
                    
                    # Extract tag number from filename (e.g., 'AV-21707_page_1.jpg' -> 'AV-21707')
                    # This regex tries to capture common valve tag patterns
                    match = re.match(r'([A-Z]{1,3}-\d{3,5}[A-Z]?)', file_name, re.IGNORECASE)
                    tag_number = match.group(1) if match else None

                    if tag_number:
                        try:
                            valve = Valve.objects.get(tag_number__iexact=tag_number)
                            
                            # Check if image already linked to avoid duplicates
                            if not ValveImage.objects.filter(valve=valve, image=full_path).exists():
                                # Create ValveImage instance
                                # Note: Django's ImageField expects a path relative to MEDIA_ROOT
                                # or a File object. We'll use a File object for existing files.
                                with open(full_path, 'rb') as f:
                                    valve_image = ValveImage(valve=valve)
                                    valve_image.image.save(file_name, File(f), save=True)
                                linked_count += 1
                                self.stdout.write(f"Successfully linked {file_name} to Valve {valve.tag_number}")
                            else:
                                self.stdout.write(f"Skipped {file_name}: Already linked to Valve {valve.tag_number}")

                        except Valve.DoesNotExist:
                            self.stdout.write(f"Warning: Valve with tag_number '{tag_number}' not found for image {file_name}")
                            skipped_count += 1
                        except Exception as e:
                            self.stdout.write(f"Error linking {file_name}: {e}")
                            skipped_count += 1
                    else:
                        self.stdout.write(f"Warning: Could not extract tag number from filename: {file_name}")
                        skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"Image linking complete. Linked: {linked_count}, Skipped: {skipped_count}"))
