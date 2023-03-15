from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken



# Create your models here.
# class BaseModel(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_delete = models.BooleanField(default=False)

#     class Meta:
#         abstract = True


class UserManager(BaseUserManager):
    def create_user(
        self,
        username,
        contact=None,
        name=None,
        is_verified=False,
        password=None,
        email=None,
        last_name=None
    ):
        if username is None:
            raise TypeError("User should have a username")
        user = self.model(
            username=username,
            name=name,
            is_verified=is_verified,
            # contact=contact,
            email=email,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        username,
        # contact="9174811701",
        name=None,
        email=None,
        # auth_provider="email",
        is_verified=True,
        password=None,
    ):
        if password is None:
            raise TypeError("Password should not be None")

        user = self.create_user(
            username=username,
            # contact=contact,
            email=email,
            name=username,
            # auth_provider=auth_provider,
            is_verified=True,
            password=password,
            last_name="admin",
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

AUTH_PROVIDERS = {"google": "google", "email": "email"}

class User(AbstractBaseUser, PermissionsMixin):
    USER_CHOICES = (
        ("google", "google"),
        ("contact", "contact"),
    )
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # employee_id = models.CharField(
    #     max_length=255, unique=True, default="--------")
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True,db_index=True, default="N/A")
    manager = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subordinates"
    )
    designation = models.CharField(max_length=255, default="N/A")
    Gender = (
        ("--/--","--/--"),
        ("female", "female"),
        ("male", "male"),
    ) 
    gender = models.CharField(max_length=255, choices=Gender, default="")  
    profile_pic = models.ImageField(blank=True, upload_to="profile_pics") 
    contact = models.CharField(max_length=255, default="N/A")
    work_from_home = models.BooleanField(default=False)
    tech_stack = models.TextField(default="N/A")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dob = models.DateField(null=True, blank=True)
    auth_provider = models.CharField(
        max_length=255, blank=False, null=False, choices=USER_CHOICES, default="email"
    )
    # team = models.ForeignKey(Team, )
    password = models.CharField(max_length=255, default="")
    # AUTH_TOKEN_EXPIRY_SECONDS = getattr(settings, 'AUTH_TOKEN_EXPIRY_SECONDS', 300)  # default 5 minutes
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    objects = UserManager()

    def __str__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
    
class Project(models.Model):
    name = models.CharField(max_length=255, default="N/A")
    program_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='managed_projects', null=True)
    employees = models.ManyToManyField(User)
    start_date = models.DateField()
    end_date = models.DateField()
    technologies_used = models.TextField(default="[]")
    client = models.CharField(max_length=255, default="N/A")
    Project_choice = [
        ('internal', 'Internal'),
        ('builder', 'Builder'),
    ]

    def __str__(self):
        return self.name


# class ProjectMembership(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.project.name


class Team(models.Model):
    name = models.CharField(max_length=255, default="N/A")
    employees = models.ManyToManyField(User)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='managed_teams', null=True)

    def __str__(self):
        return self.name



# class TeamMembership(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.team.name


class TimeSheet(models.Model):
    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='timesheets')
    date = models.DateField()

    def __str__(self):
        # return f"{self.employee} - {self.project}"
        return f"{self.employee.name}'s timesheet on {self.date}"


class Project_report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    timesheet = models.ForeignKey(TimeSheet, on_delete=models.CASCADE)
    hours_given = models.FloatField(null=True)
    billable = models.TextField(default="N/A")

    def __str__(self):
        return f"{self.timesheet.employee.name}"


# class BlacklistToken(models.Model):
#     token = models.CharField(max_length=500, unique=True)
#     blacklisted_on = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.token}"

#     @staticmethod
#     def check_blacklist(auth_token):
#         # check whether auth token has been blacklisted
#         res = BlacklistToken.objects.filter(token=str(auth_token)).first()
#         if res:
#             return True
#         else:
#             return False

class VerifyContact(models.Model):
    contact = models.CharField(max_length=15, default="N/A")
    otp = models.CharField(max_length=255)
    email = models.CharField(max_length=40, default="N/A")