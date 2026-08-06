from django.db import models
from django.conf import settings
from django.utils.text import slugify

from apps.accounts.constants import GRADE_LEVEL_CHOICES


class Subject(models.Model):
    """
    Subject model for organizing courses.
    Example:
        Mathematics
        Physics
        Chemistry
        English
    """

    name = models.CharField(
        max_length=100,
    )

    grade_level = models.CharField(
        max_length=10,
        choices=GRADE_LEVEL_CHOICES[1:],  # skip blank option
        default='G1',
        help_text="Grade level this subject belongs to"
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Example: MATH-G1, ENG-G10"
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to="subjects/",
        blank=True,
        null=True
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        default="fas fa-book"
    )

    color = models.CharField(
        max_length=20,
        default="#0d6efd",
        help_text="Hex color code"
    )

    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_subjects",
        blank=True,
        limit_choices_to={"role": "teacher"},
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
        ordering = ["grade_level", "name"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        unique_together = ("name", "grade_level")

    def __str__(self):
        return f"{self.name} — {self.get_grade_level_display()}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.grade_level}")
        super().save(*args, **kwargs)