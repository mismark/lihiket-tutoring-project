
from django.urls import path
from . import views

app_name = "subjects"

urlpatterns = [
    path("", views.subject_list, name="subject_list"),
    path("create/", views.subject_create, name="subject_create"),
    path("<slug:slug>/", views.subject_detail, name="subject_detail"),
    path("<slug:slug>/update/", views.subject_update, name="subject_update"),
    path("<slug:slug>/delete/", views.subject_delete, name="subject_delete"),
]