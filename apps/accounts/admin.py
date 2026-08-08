from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # -----------------------------
    # LIST DISPLAY
    # -----------------------------

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "phone",
        "approval_status",
        "is_staff",
        "is_active",
    )

    # -----------------------------
    # FILTERS
    # -----------------------------

    list_filter = (
        "role",
        "approval_status",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    # -----------------------------
    # SEARCH
    # -----------------------------

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    # -----------------------------
    # USER EDIT PAGE
    # -----------------------------

    fieldsets = UserAdmin.fieldsets + (

        (
            "Registration Approval",
            {
                "fields": (
                    "approval_status",
                )
            },
        ),

        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "phone",
                    "profile_picture",
                    "bio",
                    "date_of_birth",
                    "address",
                    "grade_level",
                    "cv_document",
                )
            },
        ),

    )

    # -----------------------------
    # ADD USER PAGE
    # -----------------------------

    add_fieldsets = UserAdmin.add_fieldsets + (

        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "email",
                    "phone",
                    "approval_status",
                )
            },
        ),

    )

    # -----------------------------
    # ADMIN ACTIONS
    # -----------------------------

    actions = [
        "approve_users",
        "reject_users",
    ]

    @admin.action(description="Approve selected users")
    def approve_users(self, request, queryset):

        updated = queryset.update(
            approval_status="approved"
        )

        self.message_user(
            request,
            f"{updated} user(s) approved successfully."
        )

    @admin.action(description="Reject selected users")
    def reject_users(self, request, queryset):

        updated = queryset.update(
            approval_status="rejected"
        )

        self.message_user(
            request,
            f"{updated} user(s) rejected successfully."
        )