from django.db import models
from django.conf import settings
from apps.courses.models import Course


class Assignment(models.Model):
    """
    Assignment created by a teacher for a course.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    file = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True
    )

    due_date = models.DateTimeField()

    max_marks = models.PositiveIntegerField(
        default=100
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assignments"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class AssignmentSubmission(models.Model):
    """
    Student submission for an assignment.
    """

    STATUS_CHOICES = (
        ("submitted", "Submitted"),
        ("graded", "Graded"),
        ("late", "Late"),
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions"
    )

    file = models.FileField(
        upload_to="submissions/"
    )

    remarks = models.TextField(
        blank=True
    )

    marks = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    grade = models.CharField(
        max_length=2,
        blank=True,
        help_text="Letter grade (A, B, C, D, F)"
    )

    feedback = models.TextField(
        blank=True
    )

    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_assignments",
        limit_choices_to={"role": "teacher"},
    )

    graded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="submitted"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"
        unique_together = ("assignment", "student")

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"