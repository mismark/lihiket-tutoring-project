from django.contrib import admin
from apps.accounts.permissions import has_course_access

from .models import (
    Quiz,
    Question,
    Choice,
    QuizAttempt,
    StudentAnswer,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "created_by",
        "duration",
        "passing_score",
        "is_active",
        "created_at",
    )

    list_filter = (
        "course",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "course__title",
        "created_by__username",
    )

    autocomplete_fields = (
        "course",
        "created_by",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        QuestionInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(course__subject__teachers=request.user)
        return qs


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question_text",
        "quiz",
        "question_type",
        "marks",
    )

    list_filter = (
        "question_type",
        "quiz",
    )

    search_fields = (
        "question_text",
        "quiz__title",
    )

    autocomplete_fields = (
        "quiz",
    )

    inlines = [
        ChoiceInline,
    ]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = (
        "choice_text",
        "question",
        "is_correct",
    )

    list_filter = (
        "is_correct",
    )

    search_fields = (
        "choice_text",
        "question__question_text",
    )

    autocomplete_fields = (
        "question",
    )


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "quiz",
        "score",
        "total_marks",
        "passed",
        "started_at",
        "completed_at",
    )

    list_filter = (
        "passed",
        "quiz",
    )

    search_fields = (
        "student__username",
        "quiz__title",
    )

    autocomplete_fields = (
        "student",
        "quiz",
    )

    ordering = (
        "-started_at",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(quiz__course__subject__teachers=request.user)
        return qs


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "attempt",
        "question",
        "selected_choice",
        "is_correct",
    )

    list_filter = (
        "is_correct",
    )

    autocomplete_fields = (
        "attempt",
        "question",
        "selected_choice",
    )