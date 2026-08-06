from django.urls import path

from . import views


app_name = "quizzes"


urlpatterns = [

    # ==========================
    # Quiz
    # ==========================

    path(
        "",
        views.QuizListView.as_view(),
        name="quiz_list",
    ),

    path(
        "my/",
        views.MyQuizzesView.as_view(),
        name="my_quizzes",
    ),

    path(
        "create/",
        views.QuizCreateView.as_view(),
        name="quiz_create",
    ),

    path(
        "<int:pk>/",
        views.QuizDetailView.as_view(),
        name="quiz_detail",
    ),

    path(
        "<int:pk>/update/",
        views.QuizUpdateView.as_view(),
        name="quiz_update",
    ),

    path(
        "<int:pk>/delete/",
        views.QuizDeleteView.as_view(),
        name="quiz_delete",
    ),
    
    path(
        "<int:quiz_id>/results/",
        views.quiz_results,
        name="quiz_results",
    ),

    # ==========================
    # Student Quiz
    # ==========================

    path(
        "<int:pk>/start/",
        views.start_quiz,
        name="start_quiz",
    ),

    path(
        "attempt/<int:pk>/submit/",
        views.submit_quiz,
        name="submit_quiz",
    ),

    path(
        "attempt/<int:pk>/result/",
        views.quiz_result,
        name="quiz_result",
    ),
    
    # ==========================
    # Question Management
    # ==========================

    path(
        "<int:quiz_pk>/questions/",
        views.QuestionListView.as_view(),
        name="question_list",
    ),

    path(
        "<int:quiz_pk>/questions/create/",
        views.QuestionCreateView.as_view(),
        name="question_create",
    ),

    path(
        "<int:quiz_pk>/questions/import/",
        views.import_from_question_bank,
        name="import_questions",
    ),

    path(
        "questions/<int:pk>/update/",
        views.QuestionUpdateView.as_view(),
        name="question_update",
    ),

    path(
        "questions/<int:pk>/delete/",
        views.QuestionDeleteView.as_view(),
        name="question_delete",
    ),
    
    # ==========================
# Choice Management
# ==========================

path(
    "questions/<int:question_pk>/choices/",
    views.ChoiceListView.as_view(),
    name="choice_list",
),

path(
    "questions/<int:question_pk>/choices/create/",
    views.ChoiceCreateView.as_view(),
    name="choice_create",
),

path(
    "choices/<int:pk>/update/",
    views.ChoiceUpdateView.as_view(),
    name="choice_update",
),

path(
    "choices/<int:pk>/delete/",
    views.ChoiceDeleteView.as_view(),
    name="choice_delete",
),

]