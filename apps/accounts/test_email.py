from django.core.mail import send_mail
from django.conf import settings

def send_test_email():
    send_mail(
        subject="Online Tutoring Test",
        message="Email configuration is working.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )