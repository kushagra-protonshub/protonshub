import random
import urllib
import requests
from .models import User, VerifyContact
from django.conf import settings
from django.contrib.auth import authenticate
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from common import app_logger, rest_utils
from rest_framework.response import Response
from django.http import HttpResponse
import requests

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
verify = client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID)

logger = app_logger.createLogger("app")

from django.core.mail import send_mail

def send_otp_email(email, otp):
    subject = 'Your OTP'
    message = f'Your OTP is: {otp}'
    from_email = 'example@example.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def create_user(user, request_data):
    result, message, data = False, "Failed", None
    try:
        user.set_password(request_data.get("password"))
        user = user.save()
        # send user contact OTP
        result, message, data = True, "User created successfully", None
    except Exception as e:
        result, message, data = False, str(e), None
    return result, message, data


def update_user_password(user, request_data):
    result, message, data = False, "Failed", None
    try:
        user.set_password(request_data.get("new_password"))
        user.save()
        result, message, data = True, "password changed successfully", None
    except Exception as e:
        result, message, data = False, str(e), None
    return result, message, data


def register_social_user(provider, user_id, email, name,last_name):
    filtered_user_by_email = User.objects.filter(
        username=email, email=email, auth_provider="google"
    )

    if filtered_user_by_email.exists():
        registered_user = authenticate(username=email, password=user_id)

        return {
            "username": registered_user.username,
            "email": registered_user.email,
            "tokens": registered_user.tokens(),
            "id":registered_user.id
        }

    else:
        user = {
            "username": email,
            "name": name,
            "email": email,
            "password": user_id,
            "is_verified": True,
            "auth_provider": provider,
            "last_name": last_name,
        }
        new_user = User.objects.create_user(**user)
        return {
            "email": new_user.email,
            "username": new_user.username,
            "tokens": new_user.tokens(),
            "id":new_user.id
        }

def user_message_send(phone):
    try:
        otp = random.randint(0,99999)
        verify_contact = VerifyContact.objects.create(contact=phone,otp=otp)
        message = f"Dear User, Your OTP {otp} for SHEKUNJ Regards.%0AShekunj"
        values = {'authkey' :settings.SMS_AUTH_TOKE , 'mobiles' : f'91{phone}', 'message' : message, 'sender' : "Shkunj", 'route' : 4, 'DLT_TE_ID':settings.SMS_DLT_ID  }
        postdata = urllib.parse.urlencode(values)
        res = requests.get(settings.SEND_SMS_URL,params=postdata)
        logger.debug(f'Successfully sent OTP for {phone} >>>>>>> Result >>>>>> {res.text}')

        # client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
        #     to="+91" + phone, channel="sms"
        # )
        result, message, data = True, "User OTP successfully send", None
    except Exception as e:
        result, message, data = False, str(e), None
    return result, message, data


def user_check_otp(email, code):
    try:
        verifiy = VerifyContact.objects.filter(email=email).last()
        if verifiy:
            if verifiy.otp == str(code):
                return True

        # verify_status = client.verify.services(
        #     settings.TWILIO_VERIFY_SERVICE_SID
        # ).verification_checks.create(to="+91" + phone, code=code)

        return False
    except TwilioRestException as e:
        return False


def verify_contact_otp(request_data):
    result, message, data = False, "Failed", None
    email = request_data.get("email", None)
    otp = request_data.get("otp", None)
    # user = User.objects.get(contact=phone)
    verify = user_check_otp(email, otp)

    if verify:
        # user.is_verified = True
        # user.save()
        result, message, data = True, "Successfully Verified", None
    else:
        result, message, data = False, "Invalid OTP", None
    return result, message, data


def send_email(phone):
    try:
        client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
            to="+91" + phone, channel="sms"
        )
        result, message, data = True, "User OTP successfully send", None
    except Exception as e:
        result, message, data = False, str(e), None
    return result, message, data



def forget_user_password(user, random_password):
    result, message, data = False, "Failed", None
    try:
        
        user.set_password(str(random_password))
        user.save()
        result, message, data = True, "forget password successfully", None
    except Exception as e:
        result, message, data = False, str(e), None
    return result, message, data



# def forget_password_message_send(email,random_password,request):
#     result, message, data = False, "Failed", None
#     # try:
#     #     message = f"Dear User, Your OTP new password {random_password} for protonshub"
#     #     values = {'authkey' :settings.SMS_AUTH_TOKE , 'mobiles' : f'91{phone}', 'message' : message, 'sender' : "Shkunj", 'route' : 4, 'DLT_TE_ID':settings.SMS_DLT_ID  }
#     #     postdata = urllib.parse.urlencode(values)
#     #     res = requests.get(settings.SEND_SMS_URL,params=postdata)

#     #     logger.debug(f'Successfully sent new password for {phone} >>>>>>> Result >>>>>> {res.text}')

#     #     # client.messages.create(to="+91" + phone, from_ = settings.TWILIO_NUMBER,  body=f"Hello there, {random_password}!")
#     #     result, message, data = True, "New password sent on your contact number.", None
#     # except Exception as e:
#     #     result, message, data = False, str(e), None
#     # return result, message, data



#     subject = "Protonshub forgot-password"
#     message = f"Dear User, Your OTP new password {random_password} for protonshub"
#     from_email = 'kushagra.j@protonshub.in'
#     recipient = request.data['email']
#     recipient = email
    
#     try:
#         send_mail(subject=subject,message=message,from_email=from_email,recipient_list=[recipient],fail_silently=False,)
#         return HttpResponse('Email sent successfully.')
#     except Exception as e:
#         return HttpResponse(f'Error sending email: {e}')


def forget_password_message_send(random_password, request):
    result, message, data = False, "Failed", None
    
    try:
        # Send email
        subject = "Protonshub forgot-password"
        message = f"Dear User, Your OTP new password {random_password} for protonshub"
        from_email = 'kushagra.j@protonshub.in'
        recipient = request.data['email']
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=[recipient], fail_silently=False,)
        
        result, message, data = True, "New password sent successfully.", None
    except Exception as e:
        result, message, data = False, str(e), None
    
    return result, message, data