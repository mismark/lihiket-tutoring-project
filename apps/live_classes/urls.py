from django.urls import path

from . import views

app_name = "live_classes"

urlpatterns = [

    # AJAX: load lessons for selected course
    path(
        "ajax/lessons/",
        views.ajax_load_lessons,
        name="ajax_load_lessons",
    ),

    # List all live classes
    path(
        "",
        views.live_class_list,
        name="live_class_list",
    ),

    # Teacher's live classes
    path(
        "my-live-classes/",
        views.my_live_classes,
        name="my_live_classes",
    ),

    # Upcoming classes
    path(
        "upcoming/",
        views.upcoming_classes,
        name="upcoming_classes",
    ),

    # Create live class
    path(
        "create/",
        views.live_class_create,
        name="live_class_create",
    ),

    # Join live class
    path(
        "<int:pk>/join/",
        views.join_live_class,
        name="join_live_class",
    ),

    # Live class detail
    path(
        "<int:pk>/",
        views.live_class_detail,
        name="live_class_detail",
    ),

    # Update live class
    path(
        "<int:pk>/update/",
        views.live_class_update,
        name="live_class_update",
    ),

    # Delete live class
    path(
        "<int:pk>/delete/",
        views.live_class_delete,
        name="live_class_delete",
    ),

]