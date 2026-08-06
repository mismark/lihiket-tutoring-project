from django.contrib import admin
from django.utils.html import format_html

from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "name",
        "grade_level",
        "code",
        "get_teachers",
        "is_active",
        "created_at",
    )

    list_filter = (
        "grade_level",
        "is_active",
        "teachers",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
        "grade_level",
        "teachers__username",
        "teachers__first_name",
        "teachers__last_name",
    )

    filter_horizontal = ('teachers',)

    prepopulated_fields = {
        "slug": ("name",)
    }

    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview_large",
    )

    ordering = (
        "name",
    )

    list_per_page = 20

    fieldsets = (

        (
            "Subject Information",
            {
                "fields": (
                    "name",
                    "grade_level",
                    "code",
                    "slug",
                    "description",
                )
            },
        ),

        (
            "Appearance",
            {
                "fields": (
                    "image",
                    "image_preview_large",
                    "icon",
                    "color",
                )
            },
        ),

        (
            "Teachers",
            {
                "fields": (
                    "teachers",
                )
            },
        ),

        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:8px;object-fit:cover;">',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Image"

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="200" style="border-radius:10px;">',
                obj.image.url,
            )
        return "No Image"

    image_preview_large.short_description = "Preview"

    def get_teachers(self, obj):
        return ", ".join([teacher.username for teacher in obj.teachers.all()])
    get_teachers.short_description = "Teachers"