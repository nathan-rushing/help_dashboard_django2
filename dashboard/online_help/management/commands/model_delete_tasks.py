from django.core.management.base import BaseCommand
from django.db import connection

# Delete Task with reset ID
class Command(BaseCommand):
    help = 'Delete all Task entries and reset auto-increment ID (SQLite only)'

    def handle(self, *args, **kwargs):
        from online_help.models import Task

        deleted, _ = Task.objects.all().delete()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='online_help_task';")

        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} Task entries and reset ID counter.'))





# Delete Task without Reset ID

# class Command(BaseCommand):
#     help = 'Deletes all Task entries from the database'

#     def handle(self, *args, **options):
#         Task.objects.all().delete()
#         self.stdout.write(self.style.SUCCESS('All Task entries deleted successfully!'))

