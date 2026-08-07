from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.global_search, name="search"),
    path("search/ajax/", views.ajax_search, name="ajax_search"),
    path("student-list/", views.student_list, name = "student_list"),
    path("teacher-list/", views.teacher_list, name= "teacher_list"),
    path("superuser/", views.super_user, name = "superuser_list"),
    path("parents/", views.parent_list, name = "parent_list"),
    path("student/<int:id>/", views.student_detail, name = "student_detail" ),
    
]