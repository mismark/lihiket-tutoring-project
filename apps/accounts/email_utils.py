"""
Email sending utility.

Uses Brevo (formerly Sendinblue) HTTPS API when BREVO_API_KEY is set in .env.
This bypasses all SMTP port blocking since it sends over port 443 (HTTPS).

To get a free API key:
  1. Go to https://app.brevo.com/
  2. Create a free account (300 emails/day free)
  3. Go to Settings → SMTP & API → API Keys → Generate a new API key
  4. Add to .env:  BREVO_API_KEY=your_key_here
"""

import os
import requests
from django.conf import settings


def send_otp_email(recipient_email, recipient_name, otp_code):
    """
    Send the OTP reset code to the user's email.
    Uses Brevo API over HTTPS if BREVO_API_KEY is configured,
    otherwise falls back to Django's email backend (console in DEBUG).
    """
    api_key = os.getenv("BREVO_API_KEY", "").strip()

    if api_key:
        return _send_via_brevo(api_key, recipient_email, recipient_name, otp_code)
    else:
        return _send_via_django(recipient_email, recipient_name, otp_code)


def _send_via_brevo(api_key, recipient_email, recipient_name, otp_code):
    """Send via Brevo HTTPS API — works even when SMTP ports are blocked."""
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": "Online Tutoring",
            "email": os.getenv("EMAIL_HOST_USER", "noreply@example.com"),
        },
        "to": [
            {"email": recipient_email, "name": recipient_name}
        ],
        "subject": "Your Password Reset Code",
        "htmlContent": f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;
                    border:1px solid #e0e0e0;border-radius:10px;overflow:hidden;">
          <div style="background:#0d6efd;padding:24px;text-align:center;">
            <h2 style="color:#fff;margin:0;">Password Reset</h2>
          </div>
          <div style="padding:32px;">
            <p style="color:#333;font-size:15px;">Hi <strong>{recipient_name}</strong>,</p>
            <p style="color:#555;">Use the code below to reset your password.
               It expires in <strong>10 minutes</strong>.</p>
            <div style="text-align:center;margin:32px 0;">
              <span style="font-size:40px;font-weight:bold;letter-spacing:12px;
                           color:#0d6efd;background:#f0f4ff;padding:16px 32px;
                           border-radius:10px;">{otp_code}</span>
            </div>
            <p style="color:#999;font-size:13px;">
              If you did not request this, please ignore this email.
            </p>
          </div>
        </div>
        """,
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    if response.status_code not in (200, 201):
        raise Exception(
            f"Brevo API error {response.status_code}: {response.text}"
        )

    return True


def _send_via_django(recipient_email, recipient_name, otp_code):
    """Fallback: Django email backend (console in DEBUG, SMTP in production)."""
    from django.core.mail import send_mail

    send_mail(
        subject="Your Password Reset Code",
        message=(
            f"Hi {recipient_name},\n\n"
            f"Your password reset code is: {otp_code}\n\n"
            f"This code expires in 10 minutes.\n\n"
            f"If you did not request this, please ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )
    return True
