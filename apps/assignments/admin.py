from django.contrib import admin
from apps.accounts.permissions import has_course_access

from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "created_by",
        "due_date",
        "max_marks",
        "is_active",
        "created_at",
    )

    list_filter = (
        "course",
        "is_active",
        "created_at",
        "due_date",
    )

    search_fields = (
        "title",
        "course__title",
        "created_by__username",
    )

    ordering = (
        "-created_at",
    )

    autocomplete_fields = (
        "course",
        "created_by",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(course__subject__teachers=request.user)
        return qs


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "assignment",
        "student",
        "marks",
        "grade",
        "status",
        "graded_by",
        "submitted_at",
    )

    list_filter = (
        "status",
        "submitted_at",
        "graded_by",
    )

    search_fields = (
        "assignment__title",
        "student__username",
    )

    ordering = (
        "-submitted_at",
    )

    autocomplete_fields = (
        "assignment",
        "student",
        "graded_by",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(assignment__course__subject__teachers=request.user)
        return qs