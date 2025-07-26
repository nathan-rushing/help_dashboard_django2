from django.core.management.base import BaseCommand
from django.db import connection

# Delete Writers with reset ID
class Command(BaseCommand):
    help = 'Delete all Writers entries and reset auto-increment ID (SQLite only)'

    def handle(self, *args, **kwargs):
        from online_help.models import Writers

        deleted, _ = Writers.objects.all().delete()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='online_help_writers';")

        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} Writers entries and reset ID counter.'))





# Delete Wrtiers without Reset ID

# class Command(BaseCommand):
#     help = 'Deletes all Writers entries from the database'

#     def handle(self, *args, **options):
#         Writers.objects.all().delete()
#         self.stdout.write(self.style.SUCCESS('All Writers entries deleted successfully!'))

