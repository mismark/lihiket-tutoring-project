from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("",                              views.course_list,          name="course_list"),
    path("create/",                       views.course_create,        name="course_create"),
    path("my-courses/",                   views.my_courses,           name="my_courses"),
    path("<int:pk>/",                     views.course_detail,        name="course_detail"),
    path("<int:pk>/update/",              views.course_update,        name="course_update"),
    path("<int:pk>/delete/",              views.course_delete,        name="course_delete"),
    path("<int:pk>/enroll/",              views.enroll_course,        name="enroll_course"),
    path("<int:pk>/progress/",            views.update_progress,      name="update_progress"),
    path("<int:pk>/certificate/",         views.course_certificate,   name="course_certificate"),
    path("<int:pk>/certificate/download/",views.download_certificate, name="download_certificate"),
]
