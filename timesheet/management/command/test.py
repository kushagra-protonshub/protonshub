from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generates a CSV file of time sheet data for the current month'

    def handle(self, *args, **options):
        # Get the start and end dates for the current month
        print("hello")