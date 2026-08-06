from django.db import models
from django.conf import settings

from apps.subjects.models import Subject
from apps.courses.models import Course
from apps.lessons.models import Lesson


class Document(models.Model):

    VISIBILITY_CHOICES = (
        ("public", "Public"),
        ("students", "Students Only"),
        ("teachers", "Teachers Only"),
        ("private", "Private"),
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        related_name="documents",
        null=True,
        blank=True,
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_documents",
        limit_choices_to={"role": "teacher"},
    )

    file = models.FileField(
        upload_to="documents/",
    )

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="students",
    )

    download_count = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Document"

        verbose_name_plural = "Documents"

    def __str__(self):

        return self.title

    @property
    def file_name(self):

        return self.file.name.split("/")[-1]

    @property
    def file_extension(self):

        return self.file.name.split(".")[-1].lower()

    @property
    def file_size(self):

        if self.file:

            size = self.file.size

            if size < 1024:

                return f"{size} Bytes"

            elif size < 1024 * 1024:

                return f"{size / 1024:.2f} KB"

            else:

                return f"{size / (1024 * 1024):.2f} MB"

        return "0 Bytes"