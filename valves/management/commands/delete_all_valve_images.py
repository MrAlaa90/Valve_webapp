from django.core.management.base import BaseCommand
from django.db import transaction
from valves.models import ValveImage
from django.utils.translation import gettext as _

class Command(BaseCommand):
    help = _('Deletes all ValveImage objects from the database, effectively unlinking all valve images.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            '--noinput',
            action='store_true',
            dest='no_input',
            help=_('Do NOT prompt for user input of any kind.'),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        no_input = options['no_input']
        image_count = ValveImage.objects.count()

        if image_count == 0:
            self.stdout.write(self.style.SUCCESS(_("No valve images found to delete.")))
            return

        self.stdout.write(self.style.WARNING(_(f"This command will permanently delete {image_count} valve image links from the database.")))
        self.stdout.write(self.style.WARNING(_("The actual image files on disk will NOT be deleted.")))

        if not no_input:
            confirm = input(_("Are you sure you want to continue? [y/N] "))
            if confirm.lower() != 'y':
                self.stdout.write(self.style.ERROR(_("Deletion cancelled.")))
                return

        deleted_count, __ = ValveImage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(_(f"Successfully deleted {deleted_count} valve image links.")))