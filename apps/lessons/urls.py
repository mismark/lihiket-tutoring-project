from django.urls import path

from . import views

app_name = "lessons"

urlpatterns = [

    # Lesson List
    path(
        "",
        views.lesson_list,
        name="lesson_list",
    ),
    
     # Create Lesson
    path(
        "create/",
        views.lesson_create,
        name="lesson_create",
    ),
    
    
    # My Lessons
    path(
        "my-lessons/",
        views.my_lessons,
        name="my_lessons",
    ),



    # Lesson Detail
    path(
        "<slug:slug>/",
        views.lesson_detail,
        name="lesson_detail",
    ),

   
    # Update Lesson
    path(
        "<slug:slug>/update/",
        views.lesson_update,
        name="lesson_update",
    ),

    # Delete Lesson
    path(
        "<slug:slug>/delete/",
        views.lesson_delete,
        name="lesson_delete",
    ),

    
    # Preview Lesson
    path(
        "<slug:slug>/preview/",
        views.lesson_preview,
        name="lesson_preview",
    ),

]