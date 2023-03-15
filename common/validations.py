from unittest import result
from employee.models import User
from django.contrib.auth import authenticate


class Validator:
    @staticmethod
    def is_valid_gender(gender):
        result, message = False, "Shekunj only for female"
        try:
            if gender != "male":
                result, message = True, "OK"
        except Exception as e:
            message = f"{e}"
        return result, message

    @staticmethod
    def is_valid_contact_number(number):
        result, message = False, "This contact Number Already Exits"
        try:
            if not User.objects.filter(contact=number).exists():
                result, message = True, "OK"
        except Exception as e:
            message = f"{e}"
        return result, message

    @staticmethod
    def is_valid_exists_email(email):
        result, message = False, "This email already exists!"
        try:
            if not User.objects.filter(email=email).exists():
                result, message = True, "OK"
        except Exception as e:
            message = f"{e}"
        return result, message

    @staticmethod
    def is_valid_user(email, password):
        try:
            user = authenticate(username=email, password=password)
            if not user:
                return False, "Invalid credentials, please try again.", None

            if not user.is_verified:
                return False, "email is not verified", None

            # if user.auth_provider != "email":
            #     return (
            #         False,
            #         "Please continue your login using " + user.auth_provider,
            #         None,
            #     )

            if not user.is_active:
                return False, "Account disabled, contact admin", None

        except Exception as e:
            message = f"{e}"
            return result, "Ok", None
        
        print(user)  # add this line to check the value of the user object
        return True, "Ok", user

    @staticmethod
    def is_contact_already_exists(contact):
        result, message = False, "Contact number already exists!"
        try:
            if not User.objects.filter(contact=contact).exists():
                result, message = True, "OK"
        except Exception as e:
            message = f"{e}"
        return result, message



    @staticmethod
    def is_email_exists(email):
        result, message = False, "email number is not exits"
        try:
            if User.objects.filter(username=email).exists():
                result, message = True, "Ok"
            
        except Exception as e:
            message = f"{e}"
        return result, message
    