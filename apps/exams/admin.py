from django.contrib import admin
from apps.accounts.permissions import has_course_access

from .models import (
    Exam,
    ExamQuestion,
    ExamAttempt,
    ExamAnswer,
)


class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "duration",
        "passing_score",
        "start_time",
        "end_time",
        "is_active",
        "created_by",
    )

    list_filter = (
        "course",
        "is_active",
        "start_time",
    )

    search_fields = (
        "title",
        "course__title",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        ExamQuestionInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(course__subject__teachers=request.user)
        return qs


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "exam",
        "question",
    )

    list_filter = (
        "exam",
    )

    search_fields = (
        "exam__title",
        "question__question_text",
    )


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "exam",
        "score",
        "percentage",
        "passed",
        "started_at",
        "submitted_at",
    )

    list_filter = (
        "passed",
        "exam",
    )

    search_fields = (
        "student__username",
        "student__first_name",
        "student__last_name",
        "exam__title",
    )

    ordering = (
        "-started_at",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(exam__course__subject__teachers=request.user)
        return qs


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "attempt",
        "question",
        "selected_choice",
        "is_correct",
    )

    list_filter = (
        "is_correct",
    )

    search_fields = (
        "attempt__student__username",
        "question__question_text",
    )