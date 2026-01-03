from django.core.management.base import BaseCommand
from valves.models import Valve, ValveImage, Factory
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Links existing images in the media directory to the corresponding valves in the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to link images...'))

        media_root = settings.MEDIA_ROOT
        linked_images_count = 0

        # Get all valves and store them in a dictionary for quick lookup
        valves_by_tag = {valve.tag_number: valve for valve in Valve.objects.all()}

        for root, dirs, files in os.walk(media_root):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # Extract tag_number from the filename or path
                    # This is an assumption based on filenames like 'HV-33002_page_1.jpg'
                    tag_number_from_file = file.split('_page_')[0]

                    if tag_number_from_file in valves_by_tag:
                        valve = valves_by_tag[tag_number_from_file]
                        relative_path = os.path.relpath(os.path.join(root, file), media_root)

                        # Check if this image is already linked
                        if not ValveImage.objects.filter(valve=valve, image=relative_path).exists():
                            # Determine category from the path
                            category = 'Valves_Specs' # Default
                            path_parts = os.path.normpath(relative_path).split(os.sep)
                            if len(path_parts) > 2:
                                doc_type_folder = path_parts[1]
                                if 'P&ID' in doc_type_folder:
                                    category = 'P&ID'
                                elif 'Maintenance' in doc_type_folder:
                                    category = 'Maintenance_Reports'
                            
                            ValveImage.objects.create(
                                valve=valve,
                                image=relative_path,
                                category=category,
                                description=f"Linked image for {valve.tag_number}"
                            )
                            linked_images_count += 1
                            self.stdout.write(self.style.SUCCESS(f"Successfully linked {file} to valve {valve.tag_number}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Image {file} is already linked to valve {valve.tag_number}"))

        self.stdout.write(self.style.SUCCESS(f'Finished linking images. Total new images linked: {linked_images_count}'))
