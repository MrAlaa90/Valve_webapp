import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from valves.models import Valve, ValveImage
from django.utils.translation import gettext as _

class Command(BaseCommand):
    help = _('Scans the MEDIA_ROOT for existing valve images and creates ValveImage records.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=_('Do not make any changes to the database.'),
        )
        parser.add_argument(
            '--no-input',
            '--noinput',
            action='store_true',
            dest='no_input',
            help=_('Do NOT prompt for user input of any kind.'),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry-run']
        no_input = options['no_input']
        media_root = settings.MEDIA_ROOT
        
        if not os.path.isdir(media_root):
            raise CommandError(_(f"MEDIA_ROOT '{media_root}' does not exist or is not a directory."))

        self.stdout.write(self.style.NOTICE(_(f"Scanning for valve images in: {media_root}")))

        # Get valid categories from ValveImage model choices
        valid_categories = [choice[0] for choice in ValveImage._meta.get_field('category').choices]
        
        found_images_data = []
        
        # Iterate through factory directories (e.g., AFC I, AFC II, AFC III)
        for factory_name in os.listdir(media_root):
            factory_path = os.path.join(media_root, factory_name)
            if not os.path.isdir(factory_path):
                continue
            
            # Iterate through category directories (e.g., Valves_Specs, P&ID)
            for category_name in os.listdir(factory_path):
                category_path = os.path.join(factory_path, category_name)
                if not os.path.isdir(category_path) or category_name not in valid_categories:
                    self.stdout.write(self.style.WARNING(_(f"Skipping unrecognized category folder: {category_path}")))
                    continue
                
                # Iterate through valve tag number directories
                for tag_number in os.listdir(category_path):
                    valve_tag_path = os.path.join(category_path, tag_number)
                    if not os.path.isdir(valve_tag_path):
                        continue
                    
                    # Iterate through image files
                    for filename in os.listdir(valve_tag_path):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                            relative_path = os.path.join(factory_name, category_name, tag_number, filename)
                            full_image_path = os.path.join(media_root, relative_path)
                            found_images_data.append({
                                'factory_name': factory_name,
                                'category_name': category_name,
                                'tag_number': tag_number,
                                'filename': filename,
                                'relative_path': relative_path,
                                'full_path': full_image_path,
                            })

        if not found_images_data:
            self.stdout.write(self.style.SUCCESS(_("No new valve images found in the expected structure.")))
            return

        self.stdout.write(self.style.NOTICE(_(f"Found {len(found_images_data)} potential valve images.")))

        if not no_input and not dry_run:
            confirm = input(_("Are you sure you want to create ValveImage records for these files? [y/N] "))
            if confirm.lower() != 'y':
                self.stdout.write(self.style.ERROR(_("Operation cancelled.")))
                return

        created_count = 0
        skipped_count = 0
        
        for image_data in found_images_data:
            tag_number = image_data['tag_number']
            relative_path = image_data['relative_path']
            category_name = image_data['category_name']
            factory_name = image_data['factory_name']

            try:
                valve = Valve.objects.get(tag_number=tag_number)
                
                # Check if an image with this relative path already exists for this valve
                if ValveImage.objects.filter(valve=valve, image=relative_path).exists():
                    self.stdout.write(self.style.WARNING(_(f"Skipping existing image: {relative_path} for valve {tag_number}")))
                    skipped_count += 1
                    continue

                if not dry_run:
                    # Create ValveImage object
                    # We need to pass the relative path to the ImageField
                    # The ImageField will then store this path relative to MEDIA_ROOT
                    ValveImage.objects.create(
                        valve=valve,
                        category=category_name,
                        image=relative_path # This is the path relative to MEDIA_ROOT
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(_(f"Created ValveImage for {relative_path} (Valve: {tag_number}, Category: {category_name})")))
                else:
                    self.stdout.write(self.style.NOTICE(_(f"[Dry Run] Would create ValveImage for {relative_path} (Valve: {tag_number}, Category: {category_name})")))

            except Valve.DoesNotExist:
                self.stdout.write(self.style.ERROR(_(f"Skipping image {relative_path}: Valve with tag number '{tag_number}' not found.")))
                skipped_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(_(f"Error processing {relative_path}: {e}")))
                skipped_count += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(_("\nDry run complete. No changes were made to the database.")))
        else:
            self.stdout.write(self.style.SUCCESS(_(f"\nOperation complete. Successfully created {created_count} ValveImage records.")))
        
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(_(f"Skipped {skipped_count} images due to errors or existing records.")))
