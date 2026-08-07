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
    path("student/<int:pk>/", views.student_detail, name = "student_detail" ),
    path("teacher/<int:pk>/", views.teacher_detail, name = "teacher_detail" ),
    
    path("student/<int:pk>/edit/", views.student_edit, name = "student_edit" ),
    
    path("student/<int:pk>/delete/", views.student_delete, name = "student_delete" ),

]