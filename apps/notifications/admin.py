from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ("title", "recipient", "notification_type", "is_read", "created_at")
    list_filter   = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__username")
    ordering      = ("-created_at",)
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(recipient=request.user)
