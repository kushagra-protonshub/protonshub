from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import ProjectSerializer, AssignedProjectsSerializer, TeamSerializer
from employee.models import User, Project, Team

class AssignedProjectsAPIView(APIView):
    """
    API endpoint that returns all the projects assigned to a user.
    """
    # authentication_classes = [SessionAuthentication, BasicAuthentication
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user=request.user
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
            project = Project.objects.filter(employees=user,name=name)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class TeamAPIView(APIView):
    """
    API endpoint that returns the details of a project assigned to a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        team= Team.objects.filter(employees=user)
        serializer = TeamSerializer(team, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    