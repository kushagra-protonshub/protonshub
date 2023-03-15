from rest_framework import serializers
from employee.models import Project, User,Team


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'program_manager' ,'start_date', 'end_date', 'technologies_used', 'client', 'Project_choice']


class AssignedProjectsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TeamSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    employees = UserSerializer(many=True)

    class Meta:
        model = Team
        fields = ['id','name','manager','employees']