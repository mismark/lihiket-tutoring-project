from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "lesson_order",
        "duration",
        "status",
        "is_preview",
        "created_at",
    )

    list_filter = (
        "status",
        "is_preview",
        "course",
    )

    search_fields = (
        "title",
        "description",
        "course__title",
    )

    ordering = (
        "course",
        "lesson_order",
    )

    list_editable = (
        "lesson_order",
        "status",
        "is_preview",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Lesson Information",
            {
                "fields": (
                    "course",
                    "title",
                    "slug",
                    "description",
                )
            }
        ),

        (
            "Media",
            {
                "fields": (
                    "thumbnail",
                    "video",
                    "video_url",
                )
            }
        ),

        (
            "Settings",
            {
                "fields": (
                    "lesson_order",
                    "duration",
                    "is_preview",
                    "status",
                )
            }
        ),

        (
            "Dates",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        ),

    )