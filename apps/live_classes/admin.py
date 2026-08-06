from django.contrib import admin

from .models import LiveClass


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "teacher",
        "platform",
        "start_datetime",
        "end_datetime",
        "status",
        "is_recorded",
        "created_at",
    )

    list_filter = (
        "platform",
        "status",
        "is_recorded",
        "course",
        "teacher",
    )

    search_fields = (
        "title",
        "description",
        "course__title",
        "teacher__username",
        "teacher__first_name",
        "teacher__last_name",
        "meeting_id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-start_datetime",
    )

    list_per_page = 20

    date_hierarchy = "start_datetime"

    autocomplete_fields = (
        "course",
        "lesson",
        "teacher",
    )

    fieldsets = (

        (
            "Live Class Information",
            {
                "fields": (
                    "title",
                    "description",
                    "course",
                    "lesson",
                    "teacher",
                )
            },
        ),

        (
            "Meeting Information",
            {
                "fields": (
                    "platform",
                    "meeting_link",
                    "meeting_id",
                    "passcode",
                )
            },
        ),

        (
            "Schedule",
            {
                "fields": (
                    "start_datetime",
                    "end_datetime",
                    "duration",
                    "maximum_students",
                )
            },
        ),

        (
            "Recording",
            {
                "fields": (
                    "is_recorded",
                    "recording_url",
                )
            },
        ),

        (
            "Status",
            {
                "fields": (
                    "status",
                    "thumbnail",
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
                ),
            },
        ),

    )