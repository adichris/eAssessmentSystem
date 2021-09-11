from django.urls import path
from .views import (
    LectureCreateView, LectureDetailView, lecture_created_view, LectureListView,
    LectureStudentScripts, QuizTemplateView, OnGoingQuizTemplateView, QuestionGroupDetailView,
    TheoryMarkingSchemeDetailView, TheoryQuestionSolution, TheoryQuestionSolutionUpdateView,
    TheoryMarkingSchemeHomeTemplateView, MarkTheoryScriptsDetailView, MarkScriptView,
    DepartmentLecturesTemplateView,
)

app_name = "lecture"
urlpatterns = [
    path("add/", LectureCreateView.as_view(), name="add"),
    path("created/", lecture_created_view, name="created"),
    path("detail/<int:pk>/", LectureDetailView.as_view(), name="detail"),
    path("list/", LectureListView.as_view(), name="list"),

    path("assessment/scripts/all/", LectureStudentScripts.as_view(), name="scripts_all"),
    path("assessment/quiz/all/", QuizTemplateView.as_view(), name="quiz_all"),
    path("assessment/quiz/on_going/", OnGoingQuizTemplateView.as_view(), name="on_going_quiz"),
    path("assessment/quiz/detial/<int:question_group_pk>/<int:course_id>/", QuestionGroupDetailView.as_view(), name="question_group_detail"),

    path("assessment/scheme/home/", TheoryMarkingSchemeHomeTemplateView.as_view(), name="scheme_home"),
    path("assessment/scheme/theory/detail/<str:course_id>/<int:question_group_pk>/", TheoryMarkingSchemeDetailView.as_view(), name="theory_scheme_detail"),
    path("assessment/scheme/theory/add/solution/<str:course_id>/<int:question_id>/<int:question_group_id>/<int:scheme_pk>/", TheoryQuestionSolution.as_view(), name="theory_solution_create"),
    path("assessment/scheme/theory/update/solution/<str:course_id>/<int:question_id>/<int:question_group_id>/<int:scheme_id>/<int:solution_pk>/", TheoryQuestionSolutionUpdateView.as_view(), name="theory_solution_update"),

    # marking
    path("assessment/mark/scrpts/<str:question_group_title>/<str:question_group_pk>/", MarkTheoryScriptsDetailView.as_view(), name="mark_scripts"),
    path("assessment/mark/<str:student__index_number>/<int:question_group_id>/<int:student_script_pk>/<int:scheme_pk>/", MarkScriptView.as_view(), name="mark_student_script"),

    # HOD
    path("in/<str:department_name>", DepartmentLecturesTemplateView.as_view(), name="department_lecture"),
]
