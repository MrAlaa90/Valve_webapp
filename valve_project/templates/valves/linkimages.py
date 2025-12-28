import re
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from valves.models import Valve, ValveImage


def safe_print(message):
    """Helper function to print messages safely, avoiding UnicodeEncodeError."""
    try:
        print(message)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(message.encode('utf-8', 'replace') + b'\n')


class Command(BaseCommand):
    help = 'Finds images in the media directory and links them to Valve objects based on tag_number.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-delete',
            action='store_true',
            help='Do not delete existing ValveImage objects before linking.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Main command logic.
        """
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.is_dir():
            raise CommandError(f"Media root directory '{media_root}' does not exist.")

        # 1. Pre-fetch all valve tag numbers for efficient lookup
        valves_map = {valve.tag_number: valve.pk for valve in Valve.objects.all()}
        self.stdout.write(f"Found {len(valves_map)} valves in the database.")

        # 2. Clear existing ValveImage objects if not disabled
        if not options['no_delete']:
            count, _ = ValveImage.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing ValveImage objects."))
        else:
            self.stdout.write(self.style.NOTICE("Skipping deletion of existing ValveImage objects."))

        # 3. Find all supported image files recursively
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
        image_paths = []
        for ext in image_extensions:
            image_paths.extend(media_root.rglob(ext))

        self.stdout.write(f"Found {len(image_paths)} images to process.")

        # 4. Process and link each image
        linked_count = 0
        not_found_count = 0
        for image_path in image_paths:
            filename = image_path.name
            base_name = image_path.stem

            # Extract potential tag numbers from filename or parent directory
            if '_page_' in base_name:
                raw_tag_numbers = base_name.split('_page_')[0]
            else:
                raw_tag_numbers = base_name

            parent_dir_name = image_path.parent.name
            # Heuristic: if parent dir name looks like a tag, prioritize it.
            if re.fullmatch(r'[A-Z0-9-]+', parent_dir_name):
                possible_tag_numbers = [parent_dir_name]
            else:
                possible_tag_numbers = re.split(r'[,/]', raw_tag_numbers)

            linked = False
            for tag_num in possible_tag_numbers:
                cleaned_tag_number = re.sub(r'[^a-zA-Z0-9-]', '', tag_num).strip()
                if not cleaned_tag_number:
                    continue

                # Use the pre-fetched map for lookup
                if cleaned_tag_number in valves_map:
                    valve_id = valves_map[cleaned_tag_number]
                    relative_image_path = image_path.relative_to(media_root)

                    # Create a new ValveImage object
                    ValveImage.objects.create(valve_id=valve_id, image=str(relative_image_path))
                    safe_print(f"  -> Linked image '{relative_image_path}' to valve '{cleaned_tag_number}'")
                    linked = True
                    linked_count += 1
                    break  # Link once and move to the next image

            if not linked:
                safe_print(f"  -> Valve not found for image '{filename}' (derived tags: '{raw_tag_numbers}')")
                not_found_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nScript finished. Linked: {linked_count}. Not found: {not_found_count}."
        ))