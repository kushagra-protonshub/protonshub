import os
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template, render_to_string
import twilio
import twilio.rest
import urllib.request
from PyPDF2 import PdfFileReader
import PyPDF2
from common import app_logger, rest_utils

import random

def generate_otp():
    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    return otp

logger = app_logger.createLogger("app")
class SendMail:
    @staticmethod
    def user_send_email(data):
        ctx = data
        html_content = render_to_string("email/user-verification-mail.html", ctx)

        mail = EmailMessage(
            subject="User Verification Mail",
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[data["to_email"]],
        )
        mail.content_subtype = "html"
        mail.send()

    @staticmethod
    def book_session_send_mail(data):
        ctx = data
        html_content = render_to_string("email/book-session-mail.html",ctx)
        email = data["to_email"]
        email_list = [
            email,
        ]
        mail = EmailMessage(
            subject="Book Session",
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_TO_EMAIL],
        )
        mail.content_subtype = "html"
        mail.send()
        
def download_file(download_url, filename):
    try:
        response = urllib.request.urlopen(download_url)
        file = open(filename + ".pdf", 'wb')
        file.write(response.read())
        return file
    except Exception as e:
        logger.error(f'dowload file methode error {e} with download url {download_url}')
        return None
    
def get_height_and_width(path,file_name):
    file=download_file(path, file_name)
    pdf = PyPDF2.PdfFileReader(file.name,"rb")
    total_pages = pdf.getNumPages()
    p = pdf.getPage(0)
    one_page_hight = p.mediaBox.getHeight()
    total_height = one_page_hight*total_pages
    width = p.mediaBox.getWidth()
    height = total_height
    if os.path.exists(f'{file.name}'):
        os.remove(f'{file.name}')
    return height,width,file