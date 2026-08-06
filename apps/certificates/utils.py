from django.core.mail import EmailMessage
from django.conf import settings



def send_certificate_email(
    student,
    certificate,
    pdf_file
):


    subject = (
        "Your Course Certificate"
    )


    message = f"""

Hello {student.get_full_name()},

Congratulations!

You have successfully completed:

{certificate.course.title}


Certificate Number:

{certificate.certificate_number}


You can verify your certificate here:

/certificates/verify/{certificate.certificate_id}/


Thank you for learning with us.

Online Tutoring Team

"""


    email = EmailMessage(

        subject,

        message,

        settings.DEFAULT_FROM_EMAIL,

        [
            student.email
        ]

    )


    email.attach(

        f"{certificate.course.title}_certificate.pdf",

        pdf_file,

        "application/pdf"

    )


    if student.email:

        email.send()