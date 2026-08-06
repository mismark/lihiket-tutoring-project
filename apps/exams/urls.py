from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [

    # Exam CRUD
    path("",                         views.ExamListView.as_view(),         name="exam_list"),
    path("create/",                  views.ExamCreateView.as_view(),       name="exam_create"),
    path("<int:pk>/",                views.ExamDetailView.as_view(),       name="exam_detail"),
    path("<int:pk>/update/",         views.ExamUpdateView.as_view(),       name="exam_update"),
    path("<int:pk>/delete/",         views.ExamDeleteView.as_view(),       name="exam_delete"),

    # Student
    path("my/",                      views.MyExamsView.as_view(),          name="my_exams"),
    path("<int:pk>/take/",           views.take_exam,                      name="take_exam"),
    path("attempt/<int:pk>/submit/", views.submit_exam,                    name="submit_exam"),
    path("attempt/<int:pk>/result/", views.exam_result,                    name="exam_result"),

    # Teacher results
    path("<int:exam_id>/results/",   views.exam_results,                   name="exam_results"),

    # Question management
    path("<int:exam_pk>/questions/",          views.ExamQuestionListView.as_view(), name="exam_question_list"),
    path("<int:exam_pk>/questions/add/",      views.add_exam_question,              name="add_exam_question"),
    path("<int:exam_pk>/questions/import/",   views.import_exam_questions,          name="import_exam_questions"),
    path("questions/<int:pk>/view/",          views.view_exam_question,             name="view_exam_question"),
    path("questions/<int:pk>/edit/",          views.edit_exam_question,             name="edit_exam_question"),
    path("questions/<int:pk>/delete/",        views.exam_question_delete,           name="exam_question_delete"),
]
