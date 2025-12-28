from django.core.management.base import BaseCommand
from valves.models import PartCode
import codecs

class Command(BaseCommand):
    help = 'Generates a report of all part codes and their related valve tag numbers.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Specifies the output file path for the report.',
        )

    def handle(self, *args, **options):
        output_file = options['output']
        original_stdout = self.stdout

        if output_file:
            # If an output file is specified, open it with UTF-8 encoding
            try:
                f = codecs.open(output_file, 'w', 'utf-8')
                self.stdout = f
            except IOError as e:
                self.stderr.write(self.style.ERROR(f'Could not open file {output_file} for writing: {e}'))
                return
        
        self.stdout.write('--- Part Code to Valve Tag Number Report ---\n')

        part_codes_with_valves = PartCode.objects.prefetch_related('associated_valves').filter(associated_valves__isnull=False).distinct()

        if not part_codes_with_valves.exists():
            self.stdout.write('No part codes with associated valves found.\n')
            if output_file:
                f.close()
            return

        for part_code in part_codes_with_valves:
            description = part_code.description if part_code.description else "No description"
            self.stdout.write(f"\nPart Code: {part_code.sap_code} ({description})\n")
            
            associated_valves = part_code.associated_valves.all()
            if associated_valves:
                self.stdout.write("  Related Valve Tag Numbers:\n")
                for valve in associated_valves:
                    self.stdout.write(f"    - {valve.tag_number}\n")
            else:
                self.stdout.write("  - No associated valves for this part code (unexpected).\n")

        self.stdout.write('\n--- Report Complete---\n')
        
        if output_file:
            f.close()
            self.stdout = original_stdout
            self.stdout.write(self.style.SUCCESS(f'Report successfully written to {output_file}'))
