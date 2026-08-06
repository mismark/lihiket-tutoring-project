from django.db import models
from django.utils.text import slugify

from apps.courses.models import Course


class Lesson(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    description = models.TextField(
        blank=True
    )

    video = models.FileField(
        upload_to="videos/lessons/",
        blank=True,
        null=True
    )

    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="YouTube or Vimeo URL"
    )

    thumbnail = models.ImageField(
        upload_to="lesson_images/",
        blank=True,
        null=True
    )

    duration = models.CharField(
        max_length=50,
        default="00:00"
    )

    lesson_order = models.PositiveIntegerField(
        default=1
    )

    is_preview = models.BooleanField(
        default=False,
        help_text="Students can watch without enrolling."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["lesson_order", "title"]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title