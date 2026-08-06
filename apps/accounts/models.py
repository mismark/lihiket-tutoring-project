from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random

from .constants import GRADE_LEVEL_CHOICES


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    grade_level = models.CharField(
        max_length=10,
        choices=GRADE_LEVEL_CHOICES,
        blank=True,
        null=True,
        help_text="Applicable for students only"
    )

    cv_document = models.FileField(
        upload_to='cv_documents/',
        blank=True,
        null=True,
        help_text="Applicable for teachers only (PDF, DOC, DOCX)"
    )

    def __str__(self):
        return self.username


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otp_codes'
    )
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        """OTP expires after 10 minutes."""
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    @classmethod
    def generate_for(cls, user):
        """Invalidate old codes and create a fresh 4-digit OTP for the user."""
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = str(random.randint(1000, 9999))
        return cls.objects.create(user=user, code=code)

    def __str__(self):
        return f"OTP {self.code} for {self.user.username}"
    
    