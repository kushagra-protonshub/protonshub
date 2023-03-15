from django.contrib import admin
from .models import *

# admin.site.register(ProjectMembership)
# admin.site.register(TeamMembership)


@admin.register(User)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "manager_of_managers")

    def manager_of_managers(self, obj):
        # print(obj.manager.id)
        if obj.manager != None:
            manager = obj.id
            manager_of_managers = User.objects.get(id=manager).manager.id
            if manager_of_managers != None:
                m = User.objects.get(id=manager_of_managers).manager

            return m
        else:
            pass


class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "team_members")

    def team_members(self, obj):
        team= list(obj.employees.values_list("name", flat=True))
        return team

admin.site.register(Team, TeamAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "project_members")

    def project_members(self, obj):
        # print(obj.manager.id)
        emp = list(obj.employees.values_list("name", flat=True))
        return emp

# class TeamEmployeeAdmin(admin.ModelAdmin):
#     list_display = ('employee', 'team')

# admin.site.register(TeamEmployeeAdmin)


admin.site.register(Project, ProjectAdmin)
admin.site.register(Project_report)

class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ("name", "project_name")

    def project_name(self, obj):
        project=list(Project_report.objects.filter(timesheet=obj).values_list("project__name",flat=True))
        return project
    # def work_done(self, obj):
    #     hours = Project_report.hours_given.first()
    def name(self, obj):
        return f"{obj.employee.name}'s timesheet on {obj.date}"  

admin.site.register(TimeSheet,TimeSheetAdmin)