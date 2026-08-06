from django.db import models
from django.conf import settings

from apps.courses.models import Course
from apps.quizzes.models import Question, Choice


class Exam(models.Model):
    title = models.CharField(max_length=255)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    description = models.TextField(blank=True)

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    passing_score = models.PositiveIntegerField(
        default=50,
        help_text="Passing percentage"
    )

    start_time = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_exams"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def end_time(self):
        """Computed: exam closes after start_time + duration minutes."""
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration)

    @property
    def is_currently_open(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def total_marks(self):
        return (
            self.questions.aggregate(
                total=models.Sum("question__marks")
            )["total"] or 0
        )


class ExamQuestion(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("exam", "question")

    def __str__(self):
        return f"{self.exam.title} - {self.question.question_text[:40]}"


class ExamAttempt(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_attempts"
    )

    score = models.PositiveIntegerField(default=0)

    percentage = models.FloatField(default=0)

    passed = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"


class ExamAnswer(models.Model):
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.question_text[:40]}"