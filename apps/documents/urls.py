from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [

    # ==========================
    # Document List
    # ==========================

    path(
        "",
        views.document_list,
        name="document_list",
    ),

    # ==========================
    # My Documents
    # ==========================

    path(
        "my-documents/",
        views.my_documents,
        name="my_documents",
    ),

    # ==========================
    # Upload Document
    # ==========================

    path(
        "create/",
        views.document_create,
        name="document_create",
    ),

    # ==========================
    # Document Detail
    # ==========================

    path(
        "<int:pk>/",
        views.document_detail,
        name="document_detail",
    ),

    # ==========================
    # Update Document
    # ==========================

    path(
        "<int:pk>/update/",
        views.document_update,
        name="document_update",
    ),

    # ==========================
    # Delete Document
    # ==========================

    path(
        "<int:pk>/delete/",
        views.document_delete,
        name="document_delete",
    ),

    # ==========================
    # Download Document
    # ==========================

    path(
        "<int:pk>/download/",
        views.download_document,
        name="download_document",
    ),
    
    
    # to loade a course and lessons match with subjects 
    
    path(
    "ajax/load-courses/",
    views.load_courses,
    name="load_courses",
),

path(
    "ajax/load-lessons/",
    views.load_lessons,
    name="load_lessons",
),

]