from django.db import models
from django.conf import settings


class QuestionBank(models.Model):
    """
    Reusable question bank.
    Teachers create questions here for later use in exams, quizzes and assignments.
    """

    MCQ       = "mcq"
    TRUE_FALSE = "tf"
    SHORT_ANSWER = "sa"
    ESSAY     = "essay"

    QUESTION_TYPES = (
        (MCQ,          "Multiple Choice"),
        (TRUE_FALSE,   "True / False"),
        (SHORT_ANSWER, "Short Answer"),
        (ESSAY,        "Essay"),
    )

    DIFFICULTY_LEVELS = (
        ("easy",   "Easy"),
        ("medium", "Medium"),
        ("hard",   "Hard"),
    )

    # Lazy string reference avoids circular import; SET_NULL so deleting a
    # subject does NOT cascade-delete questions.
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.SET_NULL,
        related_name="questions",
        null=True,
        blank=True,
    )

    question_text = models.TextField()

    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        default=MCQ,
    )

    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_LEVELS,
        default="medium",
    )

    marks = models.PositiveIntegerField(
        default=1,
    )

    explanation = models.TextField(
        blank=True,
        help_text="Explanation shown after the question is answered",
    )

    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated tags, e.g. algebra, fractions",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_bank_questions",
        limit_choices_to={"role": "teacher"},
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Question"
        verbose_name_plural = "Question Bank"

    def __str__(self):
        return self.question_text[:80]

    def get_type_badge_color(self):
        return {
            self.MCQ:          "primary",
            self.TRUE_FALSE:   "info",
            self.SHORT_ANSWER: "warning",
            self.ESSAY:        "secondary",
        }.get(self.question_type, "secondary")

    def get_difficulty_badge_color(self):
        return {
            "easy":   "success",
            "medium": "warning",
            "hard":   "danger",
        }.get(self.difficulty, "secondary")


class QuestionBankChoice(models.Model):
    """Answer choices for MCQ and True/False questions."""

    question = models.ForeignKey(
        QuestionBank,
        on_delete=models.CASCADE,
        related_name="choices",
    )

    choice_text = models.CharField(max_length=255)
    is_correct  = models.BooleanField(default=False)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.choice_text
