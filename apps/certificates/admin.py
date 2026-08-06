from django.contrib import admin

from .models import Certificate



@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):


    list_display = (
        "certificate_number",
        "student",
        "course",
        "issued_at",
    )


    list_filter = (
        "issued_at",
        "course",
    )


    search_fields = (
        "certificate_number",
        "student__username",
        "student__first_name",
        "student__last_name",
        "course__title",
    )


    readonly_fields = (
        "certificate_id",
        "issued_at",
    )


    ordering = (
        "-issued_at",
    )
    
    fieldsets = (

    (
        "Certificate Information",
        {
            "fields": (
                "certificate_number",
                "certificate_id",
                "issued_at",
            )
        }
    ),


    (
        "Owner",
        {
            "fields": (
                "student",
                "course",
            )
        }
    ),

)