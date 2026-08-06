from django.urls import path

from . import views

app_name = "assignments"

urlpatterns = [

    # Assignment CRUD
    path(
        "",
        views.AssignmentListView.as_view(),
        name="assignment_list",
    ),

    path(
        "<int:pk>/",
        views.AssignmentDetailView.as_view(),
        name="assignment_detail",
    ),

    path(
        "create/",
        views.AssignmentCreateView.as_view(),
        name="assignment_create",
    ),

    path(
        "<int:pk>/update/",
        views.AssignmentUpdateView.as_view(),
        name="assignment_update",
    ),

    path(
        "<int:pk>/delete/",
        views.AssignmentDeleteView.as_view(),
        name="assignment_delete",
    ),

    # Student
    path(
        "my-assignments/",
        views.MyAssignmentsView.as_view(),
        name="my_assignments",
    ),

    path(
        "<int:pk>/submit/",
        views.submit_assignment,
        name="submit_assignment",
    ),

    # Teacher
    path(
        "submission/<int:pk>/grade/",
        views.grade_submission,
        name="grade_submission",
    ),
    
    path(
        "submission/<int:pk>/",
        views.submission_detail,
        name="submission_detail",
    ),

]