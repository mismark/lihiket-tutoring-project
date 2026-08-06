from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "subject",
        "course",
        "lesson",
        "teacher",
        "visibility",
        "download_count",
        "created_at",
    )

    list_filter = (
        "visibility",
        "subject",
        "course",
        "teacher",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "teacher__username",
        "teacher__first_name",
        "teacher__last_name",
        "subject__name",
        "course__title",
        "lesson__title",
    )

    readonly_fields = (
        "download_count",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20

    autocomplete_fields = (
        "subject",
        "course",
        "lesson",
        "teacher",
    )

    date_hierarchy = "created_at"

    fieldsets = (

        (
            "Document Information",
            {
                "fields": (
                    "title",
                    "description",
                    "subject",
                    "course",
                    "lesson",
                    "teacher",
                )
            },
        ),

        (
            "File Information",
            {
                "fields": (
                    "file",
                    "visibility",
                )
            },
        ),

        (
            "Statistics",
            {
                "fields": (
                    "download_count",
                )
            },
        ),

        (
            "System Information",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),

    )