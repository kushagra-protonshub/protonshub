import csv
import datetime
from django.core.management.base import BaseCommand
from employee.models import TimeSheet, Project_report


class Command(BaseCommand):
    help = 'Generates a CSV file of time sheet data for the current month'

    def handle(self, *args, **options):
        # Get the start and end dates for the current month
        now = datetime.datetime.now()
        start_date = datetime.date(now.year, now.month - 1, 1)
        # if now.month == 12:
        #     end_date = datetime.date(now.year + 1, 1, 1)

        end_date = datetime.date(now.year, now.month, 1)
        time_sheets = TimeSheet.objects.filter(date__range=[start_date, end_date])
        filename = f'timesheet_{now.year}_{now.month}.csv'
        with open(filename, mode='w', newline='') as csv_file:
            fieldnames = ['Employee', 'Date', 'Project', 'Hours Given', 'Billable']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for time_sheet in time_sheets:
                project_reports = Project_report.objects.filter(timesheet=time_sheet)
                for project_report in project_reports:
                    writer.writerow({
                        'Employee': time_sheet.employee.username,
                        'Date': time_sheet.date,
                        'Project': project_report.project.name,
                        'Hours Given': project_report.hours_given,
                        'Billable': project_report.billable
                    })
        self.stdout.write(self.style.SUCCESS(f'Successfully generated CSV file: {filename}'))