from django.db import models
from django.conf import settings

from apps.subjects.models import Subject


class Course(models.Model):

    LEVEL_CHOICES = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    thumbnail = models.ImageField(
        upload_to="course_images/",
        blank=True,
        null=True
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_courses",
        limit_choices_to={"role": "teacher"},
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        related_name="courses",
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_courses",
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="beginner"
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
        ordering = ["-created_at"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"
    def __str__(self):
        return self.title

class Enrollment(models.Model):

    STATUS_CHOICES = (
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"    


class CourseProgress(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_progress",
        limit_choices_to={"role": "student"},
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )

    progress = models.PositiveIntegerField(
        default=0,
        help_text="Progress percentage (0-100)"
    )

    last_accessed = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-last_accessed"]

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.progress}%)"
    