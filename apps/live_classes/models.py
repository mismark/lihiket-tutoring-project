from django.db import models
from django.conf import settings

from apps.courses.models import Course
from apps.lessons.models import Lesson


class LiveClass(models.Model):

    PLATFORM_CHOICES = (
        ("zoom", "Zoom"),
        ("google_meet", "Google Meet"),
        ("microsoft_teams", "Microsoft Teams"),
        ("jitsi", "Jitsi Meet"),
        ("custom", "Custom"),
    )

    STATUS_CHOICES = (
        ("upcoming", "Upcoming"),
        ("live", "Live"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="live_classes",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        related_name="live_classes",
        null=True,
        blank=True,
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="live_classes",
        limit_choices_to={"role": "teacher"},
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    platform = models.CharField(
        max_length=30,
        choices=PLATFORM_CHOICES,
        default="google_meet",
    )

    meeting_link = models.URLField()

    meeting_id = models.CharField(
        max_length=100,
        blank=True,
    )

    passcode = models.CharField(
        max_length=100,
        blank=True,
    )

    thumbnail = models.ImageField(
        upload_to="live_class_images/",
        blank=True,
        null=True,
    )

    start_datetime = models.DateTimeField()

    end_datetime = models.DateTimeField()

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
    )

    maximum_students = models.PositiveIntegerField(
        default=100,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="upcoming",
    )

    is_recorded = models.BooleanField(
        default=False,
    )

    recording_url = models.URLField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["start_datetime"]
        verbose_name = "Live Class"
        verbose_name_plural = "Live Classes"

    def __str__(self):
        return f"{self.title} ({self.course.title})"

    @property
    def computed_status(self):
        """
        Real-time status based on current time:
          - upcoming  : now < start_datetime
          - live      : start_datetime <= now <= end_datetime
          - completed : now > end_datetime
          - cancelled : kept as-is if manually set
        """
        from django.utils import timezone
        if self.status == "cancelled":
            return "cancelled"
        now = timezone.now()
        if now < self.start_datetime:
            return "upcoming"
        if self.start_datetime <= now <= self.end_datetime:
            return "live"
        return "completed"

    def sync_status(self):
        """Update the stored status field to match computed_status and save."""
        new_status = self.computed_status
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])
        return self.status