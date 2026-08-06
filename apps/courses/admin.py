from django.contrib import admin
from .models import Course, Enrollment, CourseProgress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "teacher",
        "subject",
        "price",
        "level",
        "status",
        "created_at",
    )

    list_filter = (
        "level",
        "status",
        "subject",
    )

    search_fields = (
        "title",
        "description",
        "teacher__username",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(subject__teachers=request.user)
        return qs


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "course",
        "status",
        "enrolled_at",
    )

    list_filter = (
        "status",
        "course__subject",
    )

    search_fields = (
        "student__username",
        "course__title",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(course__subject__teachers=request.user)
        return qs


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "course",
        "progress",
        "last_accessed",
    )

    list_filter = (
        "progress",
        "course__subject",
    )

    search_fields = (
        "student__username",
        "course__title",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(course__subject__teachers=request.user)
        return qs    