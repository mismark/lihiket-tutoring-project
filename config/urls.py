from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.accounts import views


urlpatterns = [

    path("admin/", admin.site.urls),
    
    path("", views.home, name="home"),

    path("dashboard/", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    # Courses
    path("courses/", include("apps.courses.urls")),
    path(
    "certificates/",
    include("apps.certificates.urls")
    ),
    path("subjects/",include("apps.subjects.urls")),
        path(
        "lessons/",
        include("apps.lessons.urls"),
    ),
    path(
        "live-classes/",
        include("apps.live_classes.urls"),
    ),
    
    path(
        "documents/",
        include("apps.documents.urls"),
    ),
    
    path(
        "assignments/",
        include("apps.assignments.urls"),
    ),
    path(
        "quizzes/",
        include("apps.quizzes.urls"),
    ),
    
    path(
        "exams/", include("apps.exams.urls"),
    ),
    path(
        "payments/", include("apps.payments.urls"),
    ),
    path(
        "chat/", include("apps.chat.urls"),
    ),
    path(
        "notifications/", include("apps.notifications.urls"),
    ),
    path(
        "question-bank/", include("apps.question_bank.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
    