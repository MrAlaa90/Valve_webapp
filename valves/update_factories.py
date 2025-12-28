
import os
import sys
import django
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valve_project.settings')
django.setup()

from valves.models import Valve  # noqa: E402

def update_valve_factories():
    db_path = os.path.join(os.path.dirname(__file__), 'valves_db')
    for filename in os.listdir(db_path):
        if filename.endswith('.csv'):
            factory_name = filename.split('_')[0]
            filepath = os.path.join(db_path, filename)
            try:
                df = pd.read_csv(filepath)
                tag_numbers = df['tag_number'].tolist()
                valves_to_update = Valve.objects.filter(tag_number__in=tag_numbers)
                updated_count = valves_to_update.update(factory=factory_name)
                print(f"Updated {updated_count} valves for factory {factory_name}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

if __name__ == '__main__':
    update_valve_factories()
