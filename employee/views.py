import random
import re
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, smart_str
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
import jwt
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from django.http import HttpResponse
from geopy.geocoders import Nominatim
from common import app_logger, rest_utils
# from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token

from .api import (create_user, forget_password_message_send, forget_user_password, update_user_password, user_message_send,
                  verify_contact_otp)
from .models import User,VerifyContact
from .serializers import (ChangePasswordSerializer,
                          EmailVerificationSerializer, ForgetPasswordSerializer, LoginSerializer,
                          OTPVerificationSerializer, RegisterSerializer,
                          ResetPasswordEmailRequestSerializer,
                          SetNewPasswordSerializer, UpdateUserSerializer,
                          UserProfileSerializer, UserSendOptSerializer, LogoutSerializer)

logger = app_logger.createLogger("app")


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):

        try:
            data = request.data
            serializer = self.serializer_class(data=data)
        
            if serializer.is_valid():
                user = serializer.save(username=data.get("email"), is_verified=True)
                result, message, response_data = create_user(user, data)
                if result:
                    data = serializer.data
                    data["token"] = user.tokens().get("access")
                    data["refresh_token"] = user.tokens().get("refresh")
                    data["id"]=user.id
                    
                    return rest_utils.build_response(
                        status.HTTP_200_OK, message, data=data, errors=None
                    )
                else:
                    return rest_utils.build_response(
                        status.HTTP_400_BAD_REQUEST, message, data=None, errors=message
                    )
            else:
                return rest_utils.build_response(
                    status.HTTP_400_BAD_REQUEST,
                    rest_utils.HTTP_REST_MESSAGES["400"],
                    data=None,
                    errors=serializer.errors,
                )
            # logger.debug('Log whatever you want')
            # logger.error("Test!!")
            # logger.warning('Homepage was accessed at '+str(datetime.datetime.now())+' hours!')
        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )

class SendEmailOtpView(generics.GenericAPIView):
    def post(self, request):
        otp = random.randint(0,99999)
        subject = "Protonshb OTP"
        message = f"Your OTP for signup is {otp}"
        from_email = 'kushagra.j@protonshub.in'
        recipient = request.data['recipient']
        
        try:
            verify_contact = VerifyContact.objects.create(email=recipient,otp=otp)
            send_mail(subject=subject,message=message,from_email=from_email,recipient_list=[recipient],fail_silently=False,)
            return HttpResponse('Email sent successfully.')
        except Exception as e:
            return HttpResponse(f'Error sending email: {e}')

class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Description",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            message = "Successfully Activated"

            return rest_utils.build_response(
                status.HTTP_200_OK, message, errors=None, data=None
            )

        except jwt.ExpiredSignatureError as identifier:
            message = "Activation Link Expired"
            return rest_utils.build_response(
                status.HTTP_400_BAD_REQUEST, message, data=None, errors=str(identifier)
            )
        except jwt.exceptions.DecodeError as identifier:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                message,
                data=None,
                errors=str(identifier),
            )


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            data = request.data
            # breakpoint()
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                message = "User Successfully Login"
                return rest_utils.build_response(
                    status.HTTP_200_OK, message, data=serializer.data, errors=None
                )
            else:
                return rest_utils.build_response(
                    status.HTTP_400_BAD_REQUEST,
                    rest_utils.HTTP_REST_MESSAGES["400"],
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "You have been logged out successfully."}, status=status.HTTP_200_OK)
    
class UpdatePassword(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                user = self.get_object()
                result, message, response_data = update_user_password(user, data)
                if result:
                    return rest_utils.build_response(
                        status.HTTP_200_OK, message, data=serializer.data, errors=None
                    )
                else:
                    return rest_utils.build_response(
                        status.HTTP_400_BAD_REQUEST, message, data=None, errors=message
                    )
            else:
                return rest_utils.build_response(
                    status.HTTP_400_BAD_REQUEST,
                    rest_utils.HTTP_REST_MESSAGES["400"],
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = "Password Reset Success"
        return rest_utils.build_response(
            status.HTTP_200_OK, message, data=serializer.data, errors=None
        )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"Error": "Token is not valid, please request a new one."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return Response(
                {
                    "success": True,
                    "message": "Credentials Valid",
                    "uidb64": uidb64,
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )
        except DjangoUnicodeDecodeError as identifier:
            return Response(
                {"Error": "Token is not valid, please request a new one."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        context = {"request": request}
        serializer = self.serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": "We have sent you a link to reset your password."},
            status=status.HTTP_200_OK,
        )


class VerifyContactOtp(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer

    @swagger_serializer_method(serializer_or_field=OTPVerificationSerializer)
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                result, message, data = verify_contact_otp(request.data)
                if result:
                    return rest_utils.build_response(
                        status.HTTP_200_OK, message, errors=None, data=None
                    )

                else:
                    return rest_utils.build_response(
                        status.HTTP_400_BAD_REQUEST, message, data=None, errors=message
                    )
            else:
                return rest_utils.build_response(
                    status.HTTP_400_BAD_REQUEST,
                    rest_utils.HTTP_REST_MESSAGES["400"],
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )


class SendUserOtp(generics.GenericAPIView):
    serializer_class = UserSendOptSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                result, message, response_data = user_message_send(
                    request.data["contact"]
                )
                if result:
                    return rest_utils.build_response(
                        status.HTTP_200_OK, message, data=serializer.data, errors=None
                    )
                else:
                    return rest_utils.build_response(
                        status.HTTP_400_BAD_REQUEST, message, data=None, errors=message
                    )
            else:
                return rest_utils.build_response(
                    status.HTTP_400_BAD_REQUEST,
                    rest_utils.HTTP_REST_MESSAGES["400"],
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )


class UserProfileUpdate(generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer
    parser_classes = (MultiPartParser,)

    @swagger_serializer_method(serializer_or_field=UpdateUserSerializer)
    def put(self, request, pk, format=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = self.serializer_class(request.user, data=self.request.data)
            if serializer.is_valid():
                # profile_pic = request.FILES.get('profile_pic')
                profile_pic = request.FILES.get('profile_pic',request.user.profile_pic)
                serializer.save(profile_pic=profile_pic)
                return rest_utils.build_response(
                    status.HTTP_200_OK,
                    "User Profile Updated",
                    data=serializer.data,
                    errors=None,
                )
            else:
                return rest_utils.build_response(
                    status.HTTP_400_BAD_REQUEST,
                    rest_utils.HTTP_REST_MESSAGES["400"],
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )


class UserProfileView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get(self, request, format=None):
        try:
            # breakpoint()

            serializer = self.serializer_class(request.user)
            return rest_utils.build_response(
                status.HTTP_200_OK,
                "User profile detail",
                data=serializer.data,
                errors=None,
            )

        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )

class ForgetPasswordView(generics.GenericAPIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request):

        try:
            data = request.data
            serializer = self.serializer_class(data=data)

            if serializer.is_valid():
                user = User.objects.filter(username=data.get("email")).last()
                if user:
                    random_password = random.randint(0,999999)
                     # create method for send sms with random_password to that particular contact number
                    result, message, response_data = forget_user_password(user, random_password)
                    result, message, response_data = forget_password_message_send(random_password,request)
                    # if isinstance(response_data, tuple) and len(response_data) == 3:
                    #     result, message, response_data = response_data
                    # else:
                    #     result, message, response_data = False, "Error occurred", None
                    
                if result:
                    # data = serializer.data
                    # data["token"] = user.tokens().get("access")
                    # data["refresh_token"] = user.tokens().get("refresh")
                    return rest_utils.build_response(
                        status.HTTP_200_OK, message, data=message, errors=None
                    )
                else:
                    return rest_utils.build_response(
                        status.HTTP_400_BAD_REQUEST, message, data=None, errors=message
                    )
            else:
                return rest_utils.build_response(
                    status.HTTP_400_BAD_REQUEST,
                    rest_utils.HTTP_REST_MESSAGES["400"],
                    data=None,
                    errors=serializer.errors,
                )
            # logger.debug('Log whatever you want')
            # logger.error("Test!!")
            # logger.warning('Homepage was accessed at '+str(datetime.datetime.now())+' hours!')
        except Exception as e:
            message = rest_utils.HTTP_REST_MESSAGES["500"]
            return rest_utils.build_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            )


# class ForgetPasswordMessageSendView(generics.GenericAPIView):
#     serializer_class = ForgetPasswordMessageSerializer

#     def post(self, request):
#         try:
#             serializer = self.serializer_class(data=request.data)
#             if serializer.is_valid():
#                 result, message, response_data = forget_password_message_send(
#                     request.data["contact"]
#                 )
#                 if result:
#                     return rest_utils.build_response(
#                         status.HTTP_200_OK, message, data=serializer.data, errors=None
#                     )
#                 else:
#                     return rest_utils.build_response(
#                         status.HTTP_400_BAD_REQUEST, message, data=None, errors=message
#                     )
#             else:
#                 return rest_utils.build_response(
#                     status.HTTP_400_BAD_REQUEST,
#                     rest_utils.HTTP_REST_MESSAGES["400"],
#                     data=None,
#                     errors=serializer.errors,
#                 )

#         except Exception as e:
#             message = rest_utils.HTTP_REST_MESSAGES["500"]
#             return rest_utils.build_response(
#                 status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
#             )

# class UpdateCityView(generics.GenericAPIView):
#     serializer_class=UserProfileSerializer
#     def put(self, request,pk):
#         self.serializer_class=UserProfileSerializer
#         try:
#             user = User.objects.get(pk=pk)
#             serializer = self.serializer_class(user)
#             data=request.data
#             if user:
#                 latitude=data["latitude"]
#                 longitude=data["longitude"]
#                 geolocator = Nominatim(user_agent="geoapiExercises")
#                 location = geolocator.reverse(latitude+","+longitude)
#                 address = location.raw['address']
#                 city = address.get('city', '')
#                 if city:
#                     city = address.get('city', '')
#                 else:
#                     state_district=address.get('state_district', '')
#                     city=state_district.split(" ")
#                     city=city[0]
#                 state = address.get('state', '')
#                 user.city=city
#                 user.state=state
#                 user.save()
#                 message="user city updated"
#                 return rest_utils.build_response(
#                     status.HTTP_200_OK, message, data=serializer.data, errors=None
#                 )
#             else: 
#                 message="Please Login"
#                 return rest_utils.build_response(
#                     status.HTTP_200_OK, message, data=message, errors=None
#                 )
#         except Exception as e:
#             message = rest_utils.HTTP_REST_MESSAGES["500"]
#             return rest_utils.build_response(
#                 status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
#             )