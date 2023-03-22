from rest_framework import serializers
from employee.models import *


class ProjectSerializer(serializers.ModelSerializer):
    program_manager = serializers.SerializerMethodField()

    def get_program_manager(self, obj):
        if obj.program_manager:
            return f"{obj.program_manager.name}"
        else:
            return None

    class Meta:
        model = Project
        fields = ['id', 'name', 'program_manager', 'start_date',
                  'end_date', 'technologies_used', 'client', 'Project_choice']


class AssignedProjectsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class TeamSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    employees = UserSerializer(many=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'manager', 'employees']


class TimeSheetProjectSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta:
        model = Project_report
        fields = ['project']


class TimeSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = ['id', 'employee', 'date']


class ProjectReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project_report
        fields = ['timesheet', 'project', 'hours_given', 'billable']
