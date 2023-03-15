from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from common.validations import Validator

from .api import verify_contact_otp
from .models import User
from .utils import SendMail


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=5, write_only=True, required=True
    )
    contact = serializers.CharField(
        max_length=68, min_length=5, write_only=True, required=False
    )
    otp = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        result, message, data = verify_contact_otp(validated_data)
        if not result:
            raise serializers.ValidationError(message)

        data = validated_data.pop("otp", None)
        return super().create(validated_data)

    class Meta:
        model = User
        fields = ["email", "name", "last_name", "password", "contact", "otp"]

    def validate(self, data):
        result, message = Validator.is_valid_contact_number(data["contact"])
        if not result:
            raise serializers.ValidationError(message)

        if data["email"] != "":
            result, message = Validator.is_valid_exists_email(data["email"])
            if not result:
                raise serializers.ValidationError(message)

        return data


class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=555)
    email = serializers.CharField(max_length=555)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["token"]


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6, required=True)
    contact = serializers.CharField(max_length=555, read_only=True)
    password = serializers.CharField(max_length=68, min_length=5, required=True)
    name = serializers.CharField(max_length=255, min_length=5, read_only=True)
    tokens = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "name", "tokens", "refresh_token", "contact","id"]

    def validate(self, attrs):
        email = attrs.get("email", None)
        password = attrs.get("password", None)

        result, message, user = Validator.is_valid_user(email, password)
        if not result:
            raise serializers.ValidationError(message)

        return {
            "contact": user.contact,
            "email": user.email,
            "name": user.name,
            "tokens": user.tokens().get("access"),
            "refresh_token": user.tokens().get("refresh"),
            "password": user.password,
            "id":user.id
        }
    
class LogoutSerializer(serializers.Serializer):
    pass

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(bytes(str(user.id), "utf-8"))
            token = PasswordResetTokenGenerator().make_token(user)
            # current_site = get_current_site(request=self.context['request']).domain
            current_site = "http://localhost:3000"
            relativeLink = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            absurl = "http://" + current_site + relativeLink
            email_body = "Hello, \n Use link below to reset your password \n" + absurl
            data = {
                "email_body": email_body,
                "email_subject": "Reset your password",
                "to_email": user.email,
            }

            SendMail.user_send_email(data)
            return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True, required=True
    )
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("The Reset Link Is Invalid", 401)

            user.set_password(password)
            user.save()

        except Exception as e:
            raise serializers.ValidationError("The Reset Link Is Invalid", 401)
        return super().validate(attrs)


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("old_password", "new_password", "confirm_password")

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def validate_old_password(self, value):

        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value


class UserSendOptSerializer(serializers.Serializer):
    contact = serializers.CharField(
        max_length=68, min_length=5, write_only=True, required=True
    )

    def validate(self, data):
        result, message = Validator.is_contact_already_exists(data["contact"])
        if not result:
            raise serializers.ValidationError(message)
        return data


class UpdateUserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    def get_profile_pic(self, obj):
        if obj.profile_pic:
            return f"{settings.URL}{obj.profile_pic.url}"
        else:
            return None

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "last_name",
            "profile_pic",
            "dob",
            "highest_education",
            "stream",
            "state",
            "city",
            "contact"
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "last_name",
            "email",
            "contact",
            "manager",
            "dob",
            "profile_pic",
            "auth_provider"
        )

class ForgetPasswordSerializer(serializers.ModelSerializer):
    
    email = serializers.CharField(max_length=68, min_length=5, write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ["email"]
    def validate(self, data):
    
        result, message = Validator.is_email_exists(data["email"])
        if not result:
            raise serializers.ValidationError(message)
        return data


