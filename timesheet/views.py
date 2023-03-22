from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from employee.models import *
from django.shortcuts import get_object_or_404
import datetime
import csv
from django.http import HttpResponse, FileResponse
from common import app_logger, rest_utils
import openpyxl
from django.core.management.base import BaseCommand


class AssignedProjectsAPIView(APIView):
    """
    API endpoint that returns all the projects assigned to a user.
    """
    # authentication_classes = [SessionAuthentication, BasicAuthentication
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        assigned_projects = Project.objects.filter(employees=user)
        serializer = AssignedProjectsSerializer(assigned_projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectDetailsAPIView(APIView):
    """
    API endpoint that returns the details of a project assigned to a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, name):
        user = request.user
        try:
            project = Project.objects.filter(employees=user, name=name)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamAPIView(APIView):
    """
    API endpoint that returns the details of a project assigned to a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        team = Team.objects.filter(employees=user)
        serializer = TeamSerializer(team, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TimesheetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        date = request.query_params.get('date')
        timesheet = TimeSheet.objects.filter(employee=user, date=date)
        projects = Project_report.objects.filter(timesheet=timesheet.first())
        serializer = TimeSheetProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateTimesheetAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            date = datetime.date.today()
            timeSheet = TimeSheet.objects.create(employee=user, date=date)
            return Response(f"timesheet created for {date}", status=status.HTTP_200_OK)
        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )


class ProjectReportAPIView(APIView):

    def post(self, request, project_name):

        date = datetime.date.today()
        timesheet = get_object_or_404(
            TimeSheet, employee=request.user, date=date)
        project = get_object_or_404(Project, name=project_name)
        dict1 = request.data
        dict2 = {"timesheet": timesheet.id, "project": project.id}

        dict1.update(dict2)
        serializer = ProjectReportSerializer(data=dict1)

        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ExportUserCSVAPIView(APIView):

    def get(self, request):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            time_sheets = TimeSheet.objects.filter(date__range=[start_date, end_date], employee=request.user)

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="users.xls"'

        
            filename = "user.csv "
            with open(filename, mode='w', newline='') as csv_file:
                fieldnames = ['Employee', 'Date', 'Project', 'Hours Given', 'Billable']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                for time_sheet in time_sheets:
                    project_reports = Project_report.objects.filter(timesheet=time_sheet)
                    for project_report in project_reports:
                        writer.writerow({'Employee': time_sheet.employee.username, 'Date': time_sheet.date, 'Project': project_report.project.name, 'Hours Given': project_report.hours_given, 'Billable': project_report.billable})
    
            with open(filename, 'r') as f:
                csv_data = f.read()

            response.write(csv_data)
            return response

        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )
        

class ExportDataCSVAPIView(APIView):

    def get(self, request):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            time_sheets = TimeSheet.objects.filter(date__range=[start_date, end_date])

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="timesheet.xls"'

            # response = HttpResponse(content_type='text/csv')
            # response['Content-Disposition'] = f'attachment; filename="timesheets.csv"'

        
            filename = "cummulative.csv "
            with open(filename, mode='w', newline='') as csv_file:
                fieldnames = ['Employee', 'Date', 'Project', 'Hours Given', 'Billable']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                for time_sheet in time_sheets:
                    project_reports = Project_report.objects.filter(timesheet=time_sheet)
                    for project_report in project_reports:
                        writer.writerow({'Employee': time_sheet.employee.username, 'Date': time_sheet.date, 'Project': project_report.project.name, 'Hours Given': project_report.hours_given, 'Billable': project_report.billable})
    
            with open(filename, 'r') as f:
                csv_data = f.read()

            response.write(csv_data)
            return response

        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )
        


