from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Certificate



@login_required
def certificate_list(request):

    certificates = Certificate.objects.filter(
        student=request.user
    ).order_by('-issued_at')


    return render(
        request,
        "certificates/certificate_list.html",
        {
            "certificates": certificates
        }
    )




def verify_certificate(request, certificate_id):

    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id
    )


    return render(
        request,
        "certificates/verify_certificate.html",
        {
            "certificate": certificate
        }
    )