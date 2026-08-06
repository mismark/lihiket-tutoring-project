from django.db import models
from django.conf import settings

from apps.courses.models import Course


class Quiz(models.Model):
    """
    Quiz created by a teacher for a course.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
        default=30,
    )

    passing_score = models.PositiveIntegerField(
        default=50,
        help_text="Percentage required to pass",
    )
    
    max_attempts = models.PositiveIntegerField(default=1)
    
    

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_quizzes",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title


class Question(models.Model):

    MULTIPLE_CHOICE = "mcq"
    TRUE_FALSE = "tf"

    QUESTION_TYPES = (
        (MULTIPLE_CHOICE, "Multiple Choice"),
        (TRUE_FALSE, "True / False"),
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()

    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        default=MULTIPLE_CHOICE,
    )

    marks = models.PositiveIntegerField(
        default=1
    )

    explanation = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.question_text[:60]


class Choice(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )

    choice_text = models.CharField(
        max_length=255
    )

    is_correct = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.choice_text


class QuizAttempt(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )

    score = models.PositiveIntegerField(
        default=0
    )
    
    percentage = models.FloatField(default=0)

    total_marks = models.PositiveIntegerField(
        default=0
    )

    passed = models.BooleanField(
        default=False
    )
    
    

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-started_at"]
        unique_together = ("quiz", "student")

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class StudentAnswer(models.Model):

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )

    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    is_correct = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.id}"