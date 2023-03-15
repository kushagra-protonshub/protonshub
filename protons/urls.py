from django.urls import path
from django.contrib import admin


from employee.views import (LoginAPIView, PasswordTokenCheckAPI, RegisterView,
                            RequestPasswordResetEmail, SendUserOtp, ForgetPasswordView,
                            SetNewPasswordAPIView, UpdatePassword,SendEmailOtpView,
                            UserProfileView, VerifyContactOtp, LogoutView)
from timesheet.views import (ProjectDetailsAPIView, AssignedProjectsAPIView, TeamAPIView)
urlpatterns = [
    path('admin/', admin.site.urls),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path(
    #     "request-reset-email/",
    #     RequestPasswordResetEmail.as_view(),
    #     name="request-reset-email",
    # ),
    # path(
    #     "password-reset/<uidb64>/<str:token>/",
    #     PasswordTokenCheckAPI.as_view(),
    #     name="password-reset-confirm",
    # ),
    # path(
    #     "password-reset-complete/",
    #     SetNewPasswordAPIView.as_view(),
    #     name="password-reset-complete",
    # ),
    path("change_password/", UpdatePassword.as_view(),
         name="auth_change_password"),
    path("contact-verify/", VerifyContactOtp.as_view(), name="verify-contact-otp"),
    path("send-otp/", SendUserOtp.as_view(), name="send-otp"),
    path("send-email/", SendEmailOtpView.as_view(), name="send-email"),
    path("user-profile/", UserProfileView.as_view(), name="user-profile"),
    path("forget-password/", ForgetPasswordView.as_view(), name="forget-password"),

    path("assigned-projects/", AssignedProjectsAPIView.as_view(), name="assigned-projects"),
    path("project-details/<name>/", ProjectDetailsAPIView.as_view(), name="project-details"),
    path("team/", TeamAPIView.as_view(), name="team"),

]
