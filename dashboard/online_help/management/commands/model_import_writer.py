from django.core.management.base import BaseCommand
from online_help.models import Writers
import pandas as pd

class Command(BaseCommand):
    help = 'Import unique writers from a CSV or Excel file'

    def handle(self, *args, **kwargs):
        # Load your Excel file
        df = pd.read_excel('online_help/management/dataset/Radiant_2025.1_help_assignments_v3_cleaned.xlsx', sheet_name='2025.1')
        writers_list = df['Writer'].dropna()
        writers_list = writers_list[writers_list.str.strip() != ''].unique()

        for writer_name in writers_list:
            Writers.objects.create(
                writer_name=writer_name,
            )

        self.stdout.write(self.style.SUCCESS('Writers imported successfully!'))



# If you want to delete all rows in the Writers table before importing new data:
# class Command(BaseCommand):
#     def handle(self, *args, **options): 
#         Writers.objects.all().delete()
#         self.stdout.write(self.style.SUCCESS('Writers deleted successfully!'))