import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.courses.models import Course


class Certificate(models.Model):

    certificate_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    certificate_number = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )

    issued_at = models.DateTimeField(
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):

        if not self.certificate_number:

            self.certificate_number = (
                f"CERT-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.certificate_number