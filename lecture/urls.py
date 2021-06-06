from django.urls import path
from .views import (
    LectureCreateView, LectureDetailView, lecture_created_view, LectureListView,
    LectureStudentScripts, QuizTemplateView, OnGoingQuizTemplateView, QuestionGroupDetailView
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

]
